#!/usr/bin/env python
import csv
import os.path
from tasks import sentiment
from celery import group
from collections import (
    defaultdict,
    Counter
)
from itertools import groupby
from numpy import (
    std,
    mean,
    log
)
from prettytable import from_csv
import matplotlib.pyplot as plt


def polarity_to_class(polarity):
    if polarity > 0:
        return 'pos'
    elif polarity < 0:
        return 'neg'
    return 'neu'


def process_tweets(tweets_filename="tweets.csv", counts_filename="all_count.csv"):
    with open(tweets_filename, "rb") as rfp:
        reader = csv.reader(rfp)
        processed = group(
            sentiment.s(row)
            for row in reader
        ).apply_async().get()

    movies = defaultdict(list)
    for name, classification in processed:
        movies[name].append(classification)

    with open(counts_filename, "wb") as wfp:
        writer = csv.writer(wfp)
        columns = ["Title", "Polarity Mean", "Polarity SD", "All", "Positive", "Neutral", "Negative"]
        writer.writerow(columns)

        for movie, classifcations in sorted(
            movies.iteritems(),
            key=lambda elem: len(elem[1]),
            reverse=True
        ):

            counted = Counter(
                [polarity_to_class(polarity) for polarity in classifcations]
            )
            writer.writerow([
                movie,
                mean(classifcations),
                std(classifcations),
                len(classifcations),
                counted['pos'],
                counted['neu'],
                counted['neg'],
            ])


def mean_sd(data):
    print "Mean: {}\t SD: {}".format(mean(data), std(data))


def analyze(filename):
    with open(filename, 'rb') as fp:
        next(fp)  # skip columns
        reader = csv.reader(fp)
        counts = {
            "all": [],
            "positive": [],
            "neutral": [],
            "negative": [],
        }
        for row in reader:
            for key, value in zip(["all", "positive", "neutral", "negative"], row[3:]):
                counts[key].append(int(value))

    for key, data in counts.iteritems():
        print "{} tweets count: ".format(key)
        mean_sd(data)


def get_organic_tweets():
    """
    Without links
    """
    with open("tweets.csv", 'rb') as tfp, open("organic_tweets.csv", 'wb') as otfp:
        reader = csv.reader(tfp)
        writer = csv.writer(otfp)
        for row in reader:
            if int(row[-1]) == 0:
                writer.writerow(row)


def show_stats(filename):
    with open(filename, 'rb') as fp:
        print from_csv(fp)
    analyze(filename)


def get_influential_ppl(filename):
    print "\nMovies with influential ppl, sorted by most influential\n"
    with open(filename, "rb") as fp:
        reader = csv.reader(fp)
        tweets_by_movie = groupby(reader, lambda elem: elem[0])

        influential_by_movies = {}
        for movie, tweets in tweets_by_movie:
            ppl = []
            for tweet in tweets:
                ppl += [tweet[2]] * int(tweet[6])  # tweet author * favourite count
                if tweet[-4]:
                    ppl += [tweet[-4]] * int(tweet[5])  # original author * retweeted count
            c = Counter(ppl)
            influential_by_movies[movie] = c.most_common(5)
        for movie, most_common in sorted(
            influential_by_movies.iteritems(),
            key=lambda elem: sum([x for _, x in elem[1]]),
            reverse=True
        ):
            if most_common:
                print "Movie: {}, influential ids: {}".format(
                    movie,
                    ", ".join([key for key, _ in most_common])
                )
            else:
                print "Movie: {}, no influential ppl".format(movie)


def check_tweets_distribution():
    with open("organic_tweets.csv", "rb") as fp:
        reader = csv.reader(fp)
        ppl = [row[2] for row in reader]
    counted = Counter(ppl)
    count_distribution = Counter([counts for _, counts in counted.iteritems()])
    fig = plt.figure()
    plt.plot(
        log(count_distribution.keys()),
        log(count_distribution.values()),
        linestyle='-'
    )
    fig.suptitle("Distribution of tweets about movies 14.02.2015", fontsize=20)
    plt.xlabel(u'tweets')
    plt.ylabel(u'frequency')
    fig.savefig('test.jpg')
    plt.show()


if __name__ == '__main__':
    if not os.path.exists("all_count.csv"):
        process_tweets()
    if not os.path.exists("organic_tweets.csv"):
        get_organic_tweets()
        process_tweets("organic_tweets.csv", "organic_count.csv")
    print "All:"
    show_stats("all_count.csv")
    get_influential_ppl("tweets.csv")
    print "-"*50
    print "Organic:"
    show_stats("organic_count.csv")
    print "-"*50
    get_influential_ppl("organic_tweets.csv")
    check_tweets_distribution()

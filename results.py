#!/usr/bin/env python
import csv
from tasks import sentiment
from celery import group
from collections import (
    defaultdict,
    Counter
)
from numpy import (
    std,
    mean,
)
from prettytable import from_csv


def polarity_to_class(polarity):
    if polarity > 0:
        return 'pos'
    elif polarity < 0:
        return 'neg'
    return 'neu'


def process_tweets():
    with open("tweets.csv", "rb") as rfp:
        reader = csv.reader(rfp)
        processed = group(
            sentiment.s(row)
            for row in reader
        ).apply_async().get()

    movies = defaultdict(list)
    for name, classification in processed:
        movies[name].append(classification)

    with open("counted.csv", "wb") as wfp:
        writer = csv.writer(wfp)
        columns = ["Title", "Mean", "SD", "All", "Positive", "Neutral", "Negative"]
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

if __name__ == '__main__':
    process_tweets()
    with open("counted.csv") as fp:
        print from_csv(fp)

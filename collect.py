#!/usr/bin/env python
"""
Tool to collect tweets
To use it you need to create settings.py with:
* TWITTER_ACCESS_SECRET
* TWITTER_ACCESS_TOKEN
* TWITTER_CONSUMER_KEY
* TWITTER_CONSUMER_SECRET
"""

import tweepy
import csv
import string
import unidecode
import os.path

from datetime import (
    datetime,
    timedelta,
)
from pygeocoder import Geocoder
from settings import (
    TWITTER_ACCESS_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)


def setup_twitter_api():
    twitter_auth = tweepy.OAuthHandler(
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET,
    )
    twitter_auth.set_access_token(
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET,
    )

    return tweepy.API(twitter_auth)


def get_tweets_by(api, query, date, since_id=None, geocode=None):
    full_query = "{} since:{} until:{}".format(
        query,
        date.strftime("%Y-%m-%d"),
        (date + timedelta(days=1)).strftime("%Y-%m-%d")
    )
    cursor = tweepy.Cursor(
        api.search,
        q=full_query,
        lang='en',
        geocode=geocode,
        count=100,
        since_id=since_id,
    )
    # yielding data in order: id, user id, text, date when created, retweet count
    # favorite count, original author id or "", screen names, hashtags count, urls count
    try:
        for tweet in cursor.items():
            try:
                originial_author = tweet.retweeted_status.author.id
            except AttributeError:
                originial_author = ""
            mentions = ";".join(
                [mention['screen_name']
                 for mention in tweet.entities['user_mentions']]
            )
            hashtags = len(tweet.entities['hashtags'])
            urls = len(tweet.entities['urls'])
            yield [
                tweet.id,
                tweet.user.id,
                unidecode.unidecode(tweet.text),
                tweet.created_at,
                tweet.retweet_count,
                tweet.favorite_count,
                originial_author,
                mentions,
                hashtags,
                urls,
            ]
    except tweepy.TweepError as e:
        print e.message


def query_from_title(title):
    table = string.maketrans("", "")
    title = title.translate(table, string.punctuation)
    one_word = "".join(title.lower().split())
    return "(#{0} #movie) OR #{0}movie OR #{0}_movie".format(one_word)


def geocode_from_city(city):
    return "{},{},10km".format(*Geocoder.geocode(city)[0].coordinates)


def get_last_tweet(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as fh:
            fh.seek(-1024, 2)
            last = fh.readlines()[-1].decode()
        reader = csv.reader([last])
        return reader.next()[:2]
    return [None, None]


def get_movie_titles(filename, last_title):
    with open(filename, "rb")as rfp:
        reader = csv.reader(rfp)
        titles = [title for _, title, _, _ in reader]
    if last_title:
        return titles[titles.index(last_title.strip())+1:]
    return titles


if __name__ == '__main__':
    api = setup_twitter_api()
    last_title, since_id = get_last_tweet("tweets.csv")
    titles = get_movie_titles("./process/relevant.csv", last_title)

    with open("tweets.csv", "a+b") as twfp:
        writer = csv.writer(twfp)
        for title in titles:
            for row in get_tweets_by(
                api,
                query_from_title(title),
                datetime.now(),
                since_id
            ):
                writer.writerow([title] + row)

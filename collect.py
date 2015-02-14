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

from datetime import (
    datetime,
    timedelta,
)

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


def get_tweets_by(api, query, date, geocode=None):
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
    )
    # yielding data in order: id, user id, text, date when created, retweet count
    # favorite count, original author id or "", screen names, hashtags count, urls count
    for tweet in cursor.items():
        try:
            originial_author = tweet.retweeted_status.author.id
        except AttributeError:
            originial_author = ""
        mentions = ";".join(
            [mention['screen_name'] for mention in tweet.entities['user_mentions']]
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
            urls
        ]


def query_from_title(title):
    table = string.maketrans("", "")
    title = title.translate(table, string.punctuation)
    return "(#{0} #movie) OR #{0}movie OR #{0}_movie".format(title)


if __name__ == '__main__':
    api = setup_twitter_api()
    with open("tweets.csv", "wb") as twfp, open("./process/relevant.csv", "rb") as rfp:
        reader = csv.reader(rfp)
        writer = csv.writer(twfp)
        for _, title, _, _ in reader:
            for row in get_tweets_by(api, query_from_title(title), datetime.now()):
                writer.writerow(row)

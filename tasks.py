from celery import Celery

from textblob import TextBlob

app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')


@app.task
def sentiment(row):
    blob = TextBlob(row[3])  # tweet text
    return row[0], blob.sentiment.polarity

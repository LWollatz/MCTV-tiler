from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery('tiler',
             broker='pyamqp://guest@localhost//',
             backend='amqp',
             include=['tiler.tasks'])

if __name__ == "__main__":
    app.start()

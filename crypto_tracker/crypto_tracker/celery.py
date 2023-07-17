from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_tracker.settings')

app = Celery('crypto_tracker')
app.conf.enable_utc = False

app.conf.update(timezone = 'Europe/Vilnius')

app.config_from_object(settings, namespace='CELERY')

#CELERY BEAT SETTINGS
app.conf.beat_schedule = {
    # 'every_10_seconds': {
    #     'task': "BTCUSDT",
    #     'schedule': 10,
    #     'kwargs': {
    #         'period': 3600000,
    #         'symbol': 'BTCUSDT'
    #     }
    # },
}



app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
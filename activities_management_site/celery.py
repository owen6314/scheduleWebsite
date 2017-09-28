from __future__ import absolute_import, unicode_literals
from django.conf import settings
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'activities_management_site.settings')

app = Celery('activities_management_site')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

import django
django.setup()
from ActivitiesManager import mails
from celery.decorators import periodic_task
from celery.task.schedules import crontab

@periodic_task(
    run_every = (crontab(minute='*/1')),
    name = "task_send_remind_mails",
    ignore_result = True
)
def task_send_remind_mails():
    mails.send_remind_mails()
    print('lalala')    
'''
@app.task(bind=True)
def debug_task(self):
	print('Request:{0!r}'.format(self.request))
'''

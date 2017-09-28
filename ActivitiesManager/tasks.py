from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import periodic_task
from celery.utils.log import get_task_logger
from .mails import send_remind_mails

logger = get_task_logger(__name__)

@periodic_task(
    run_every = (crontab(minute='*/1')),
    name = "task_send_remind_mails",
    ignore_result = True
)
def task_send_remind_mails():
	send_remind_mails()
	logger.info("email sent!")

@task(bind=True)
def hello():
	print("hello")

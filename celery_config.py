from celery import Celery
from celery.schedules import crontab
from mail_service.config import CELERY_CONFIG

celery_app = Celery('booky', broker=CELERY_CONFIG['broker'])
celery_app.conf.update(CELERY_CONFIG)

celery_app.conf.beat_schedule = {
    'check-reminders-every-hour': {
        'task': 'check_and_send_reminders',
        'schedule': crontab(minute=0),
    },
}

from mail_service.tasks import send_email
from mail_service.scheduler import check_and_send_reminders

@celery_app.task(name='send_email')
def send_email_task(destination, subject, content, content_type='html'):
    return send_email(destination, subject, content, content_type)

@celery_app.task(name='check_and_send_reminders')
def check_and_send_reminders_task():
    return check_and_send_reminders()

if __name__ == '__main__':
    celery_app.start()
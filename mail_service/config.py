import os
from env_service import getenv

SMTP_CONFIG = {
    'server':   'smtp.gmail.com',
    'port':     465,
    'username': 'seniwave.agency@seniwave.com',
    'password':  getenv('EMAIL_PASSWORD'),
    'sender':   'noreply@seniwave.com'
}

CELERY_CONFIG = {
    'broker': getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    'result_backend': getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': ('UTC'),
    'enable_utc': True,
    'worker_send_task_events': True,
    'task_send_sent_event': True,
    'task_track_started': True,
    'task_time_limit': 300,
    'task_soft_time_limit': 240,
    'worker_prefetch_multiplier': 1,
    'worker_max_tasks_per_child': 1000,
    'worker_disable_rate_limits': False,
    'task_acks_late': True,
    'task_reject_on_worker_lost': True,
}

TEMPLATE_PATHS = {
    'mjml_reminder': os.path.join('static', 'email', 'template_reminder.mjml'),
    'mjml_code': os.path.join('static', 'email', 'template_code.mjml')
}
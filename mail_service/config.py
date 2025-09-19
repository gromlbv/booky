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
    'broker': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/0',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
}

TEMPLATE_PATHS = {
    'mjml_reminder': os.path.join('static', 'email', 'template_reminder.mjml'),
    'mjml_code': os.path.join('static', 'email', 'template_code.mjml')
}


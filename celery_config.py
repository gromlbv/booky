CELERY_CONFIG = {
    'task_always_eager': False,
    'worker_pool_restarts': True,
    'worker_pool': 'solo',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True
}
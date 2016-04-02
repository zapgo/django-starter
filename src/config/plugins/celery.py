from datetime import timedelta

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = "UTC"

CELERY_CREATE_MISSING_QUEUES = True

CELERY_DEFAULT_QUEUE = 'task_queue'

CELERY_ROUTES = {'starter_app.tasks.test_task': {'queue': 'test_task_queue'}}

BROKER_TRANSPORT = 'sqs'
BROKER_TRANSPORT_OPTIONS = {
    'region': 'eu-west-1',
    'visibility_timeout': 30,
    'polling_interval': 1,
}

CELERYBEAT_SCHEDULE = {
    'periodic_test_task': {
        'task': 'starter_app.tasks.test_task',
        'schedule': timedelta(seconds=30),
        'args': ()
    }
}
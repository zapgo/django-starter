from celery import shared_task

@shared_task
def test_task():
    return 'test_task'

@shared_task
def default_task():
    return 'default_task'

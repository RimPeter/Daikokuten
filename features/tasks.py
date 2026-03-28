from celery import shared_task


@shared_task
def build_features_task():
    return []

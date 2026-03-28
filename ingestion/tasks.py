from celery import shared_task


@shared_task
def fetch_market_snapshots():
    return []

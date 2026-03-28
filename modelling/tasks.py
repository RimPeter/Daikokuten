from celery import shared_task
from django.utils import timezone

from modelling.predictors import create_model_run, save_market_predictions
from markets.models import Market


@shared_task
def run_training():
    return {}


@shared_task
def generate_predictions(model_name: str = 'betlab_tennis', version: str = '', note: str = ''):
    now = timezone.now()
    model_run = create_model_run(
        name=model_name,
        version=version,
        config={'generated_at': now.isoformat()},
        note=note,
    )

    upcoming_markets = (
        Market.objects.filter(market_time__gte=now)
        .prefetch_related('snapshots__runner_snapshots')
        .order_by('market_time')
    )

    created_count = 0
    for market in upcoming_markets:
        snapshot = market.snapshots.order_by('-timestamp').first()
        if snapshot is None:
            continue

        saved_predictions = save_market_predictions(model_run, market, snapshot)
        created_count += len(saved_predictions)

    return {
        'model_run_id': model_run.id,
        'model_name': model_run.name,
        'version': model_run.version,
        'created_predictions': created_count,
    }

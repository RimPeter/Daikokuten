from django.db.models import Prefetch
from django.utils import timezone

from markets.models import Market, MarketSnapshot, RunnerSnapshot
from modelling.models import ModelRun, Prediction
from modelling.predictors import predict_market_snapshot


def upcoming_markets(limit: int = 20):
    now = timezone.now()
    return (
        Market.objects.filter(market_time__gte=now)
        .select_related('event')
        .order_by('market_time')[:limit]
    )


def market_detail(market_id):
    market = (
        Market.objects.filter(market_id=market_id)
        .select_related('event')
        .prefetch_related(
            'runners',
            Prefetch('snapshots', queryset=MarketSnapshot.objects.order_by('-timestamp')),
            Prefetch('snapshots__runner_snapshots', queryset=RunnerSnapshot.objects.order_by('selection_id')),
        )
        .first()
    )
    if not market:
        return None

    latest_snapshot = market.snapshots.first()
    runner_data = []
    predictions = []
    if latest_snapshot:
        runner_lookup = {rs.selection_id: rs for rs in latest_snapshot.runner_snapshots.all()}
        for runner in market.runners.all():
            runner_record = runner_lookup.get(runner.runner_id)
            runner_data.append({
                'runner_id': runner.runner_id,
                'name': runner.name,
                'last_price_traded': runner_record.last_price_traded if runner_record else None,
                'metadata': runner_record.metadata if runner_record else {},
            })
        predictions = predict_market_snapshot(market, latest_snapshot)

    persisted_predictions = list(
        Prediction.objects.filter(market=market)
        .order_by('-inference_time')
        .values(
            'runner_id',
            'predicted_probability',
            'predicted_odds',
            'inference_time',
            'raw_output',
        )
    )

    if persisted_predictions:
        predictions = [
            {
                'runner_id': pred['runner_id'],
                'runner_name': pred['raw_output'].get('runner_name'),
                'last_price_traded': pred['raw_output'].get('last_price_traded'),
                'predicted_probability': pred['predicted_probability'],
                'predicted_odds': pred['predicted_odds'],
                'inference_time': pred['inference_time'],
            }
            for pred in persisted_predictions
        ]
    else:
        predictions = predict_market_snapshot(market, latest_snapshot) if latest_snapshot else []

    return {
        'market': market,
        'latest_snapshot': latest_snapshot,
        'runners': runner_data,
        'predictions': predictions,
    }


def predictions(limit: int = 20):
    persisted = (
        Prediction.objects.select_related('market', 'model_run')
        .order_by('-inference_time')[:limit]
    )
    results = []
    for pred in persisted:
        results.append({
            'market': pred.market,
            'prediction': pred,
            'model_run': pred.model_run,
        })
    return results


def model_runs(limit: int = 20):
    return ModelRun.objects.order_by('-created_at')[:limit]


def model_run_detail(run_id: int):
    model_run = ModelRun.objects.filter(id=run_id).first()
    if not model_run:
        return None

    predictions = (
        Prediction.objects.filter(model_run=model_run)
        .select_related('market')
        .order_by('-inference_time')
    )

    return {
        'model_run': model_run,
        'predictions': predictions,
    }

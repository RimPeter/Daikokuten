from typing import Dict, List, Optional

from markets.models import Market, MarketSnapshot, RunnerSnapshot
from modelling.models import ModelRun, Prediction


def implied_probability(price: Optional[float]) -> float:
    if price is None or price <= 0:
        return 0.0
    return min(max(1.0 / float(price), 0.0), 1.0)


def normalize_probabilities(values: List[float]) -> List[float]:
    total = sum(values)
    if total <= 0:
        if not values:
            return []
        equal = 1.0 / len(values)
        return [equal] * len(values)
    return [float(value) / total for value in values]


def predict_market_snapshot(market: Market, snapshot: MarketSnapshot) -> List[Dict]:
    runner_snapshots = list(snapshot.runner_snapshots.all())
    probabilities = [implied_probability(rs.last_price_traded) for rs in runner_snapshots]
    normalized = normalize_probabilities(probabilities)

    predictions = []
    for rs, probability in zip(runner_snapshots, normalized):
        predicted_odds = None
        if probability > 0:
            predicted_odds = round(1.0 / probability, 3)
        predictions.append({
            'market_id': market.market_id,
            'runner_id': rs.selection_id,
            'runner_name': rs.runner.name if rs.runner else None,
            'last_price_traded': rs.last_price_traded,
            'predicted_probability': round(probability, 4),
            'predicted_odds': predicted_odds,
        })

    return sorted(predictions, key=lambda item: item['predicted_probability'], reverse=True)


def create_model_run(name: str, version: str = '', config: Optional[Dict] = None, metrics: Optional[Dict] = None, note: str = '') -> ModelRun:
    return ModelRun.objects.create(
        name=name,
        version=version,
        config=config or {},
        metrics=metrics or {},
        note=note,
    )


def save_market_predictions(model_run: ModelRun, market: Market, snapshot: MarketSnapshot) -> List[Prediction]:
    predictions = predict_market_snapshot(market, snapshot)
    saved_predictions = []
    for pred in predictions:
        saved = Prediction.objects.create(
            market=market,
            model_run=model_run,
            runner_id=pred['runner_id'],
            predicted_probability=pred['predicted_probability'],
            predicted_odds=pred['predicted_odds'],
            raw_output={
                'last_price_traded': pred['last_price_traded'],
                'runner_name': pred['runner_name'],
            },
        )
        saved_predictions.append(saved)
    return saved_predictions

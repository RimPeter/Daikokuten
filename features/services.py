from datetime import timedelta

from django.utils import timezone
from markets.models import Market


def build_feature_rows(max_markets: int = 50) -> list[dict]:
    now = timezone.now()
    rows = []
    markets = (
        Market.objects.filter(market_time__gte=now)
        .select_related('event')
        .prefetch_related('runners', 'snapshots__runner_snapshots')
        .order_by('market_time')[:max_markets]
    )

    for market in markets:
        snapshot = market.snapshots.order_by('-timestamp').first()
        if not snapshot:
            continue

        runner_snapshots = list(snapshot.runner_snapshots.all())
        prices = [rs.last_price_traded for rs in runner_snapshots if rs.last_price_traded is not None]
        if not prices:
            continue

        row = {
            'market_id': market.market_id,
            'event_id': market.event.event_id,
            'market_type': market.market_type,
            'market_time': market.market_time.isoformat() if market.market_time else None,
            'runner_count': len(runner_snapshots),
            'best_price': min(prices),
            'worst_price': max(prices),
            'price_spread': max(prices) - min(prices),
            'average_price': sum(prices) / len(prices),
            'time_until_market': (market.market_time - now).total_seconds() if market.market_time else None,
            'snapshot_age_seconds': (now - snapshot.timestamp).total_seconds(),
            'top_runner_id': runner_snapshots[0].selection_id if runner_snapshots else None,
            'prices': prices,
        }

        rows.append(row)

    return rows

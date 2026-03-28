import bz2
import json
import tarfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Generator, Optional

from django.db import transaction
from django.utils import timezone as dj_timezone
from django.utils.dateparse import parse_datetime

from markets.models import Event, Market, MarketSnapshot, Runner, RunnerSnapshot, Sport


def parse_bz2_snapshot_file(file_data: bytes) -> Generator[Dict, None, None]:
    decoded = bz2.decompress(file_data).decode('utf-8', errors='ignore')
    for raw_line in decoded.splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            yield json.loads(raw_line)
        except json.JSONDecodeError:
            continue


def iter_snapshot_files(archive_path: str, max_files: Optional[int] = None) -> Generator[bytes, None, None]:
    path = Path(archive_path)
    if not path.exists():
        raise FileNotFoundError(f'Archive not found: {archive_path}')

    with tarfile.open(path, 'r') as tar:
        count = 0
        for member in tar.getmembers():
            if not member.isfile():
                continue
            if max_files is not None and count >= max_files:
                break
            fileobj = tar.extractfile(member)
            if fileobj is None:
                continue
            yield fileobj.read()
            count += 1


def parse_timestamp(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    if isinstance(value, str):
        dt = parse_datetime(value)
        if dt is not None:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
    return None


def get_sport() -> Sport:
    return Sport.objects.get_or_create(code='TENNIS', defaults={'name': 'Tennis'})[0]


def get_or_create_event(event_id: str, sport: Sport, start_time: Optional[datetime] = None) -> Event:
    event, created = Event.objects.get_or_create(
        event_id=event_id,
        defaults={
            'sport': sport,
            'start_time': start_time,
            'name': '',
        },
    )
    if start_time and event.start_time is None:
        event.start_time = start_time
        event.save(update_fields=['start_time'])
    return event


def get_or_create_market_from_definition(market_id: str, market_definition: Dict) -> Optional[Market]:
    if not market_id or not isinstance(market_definition, dict):
        return None

    if str(market_definition.get('eventTypeId')) != '2':
        return None

    sport = get_sport()
    event = get_or_create_event(
        event_id=str(market_definition.get('eventId', '')),
        sport=sport,
        start_time=parse_timestamp(market_definition.get('marketTime')),
    )

    market, created = Market.objects.get_or_create(
        market_id=str(market_id),
        defaults={
            'event': event,
            'market_type': market_definition.get('marketType', ''),
            'market_time': parse_timestamp(market_definition.get('marketTime')),
            'suspend_time': parse_timestamp(market_definition.get('suspendTime')),
            'in_play': bool(market_definition.get('turnInPlayEnabled', False)),
            'raw_definition': market_definition,
        },
    )

    if not created:
        updated = False
        if market.raw_definition is None:
            market.raw_definition = market_definition
            updated = True
        if market.market_type == '' and market_definition.get('marketType'):
            market.market_type = market_definition.get('marketType', '')
            updated = True
        if updated:
            market.save(update_fields=['raw_definition', 'market_type'])

    if isinstance(market_definition.get('runners'), list):
        for runner_definition in market_definition['runners']:
            if not isinstance(runner_definition, dict):
                continue
            Runner.objects.get_or_create(
                market=market,
                runner_id=str(runner_definition.get('id', '')),
                defaults={
                    'name': runner_definition.get('name', ''),
                    'sort_priority': runner_definition.get('sortPriority'),
                },
            )

    return market


def find_existing_tennis_market(market_id: str) -> Optional[Market]:
    if not market_id:
        return None
    market = Market.objects.select_related('event__sport').filter(market_id=str(market_id)).first()
    if market and market.event.sport.code == 'TENNIS':
        return market
    return None


def get_tennis_market(market_payload: Dict) -> Optional[Market]:
    market_id = market_payload.get('id')
    existing_market = find_existing_tennis_market(market_id)
    if existing_market:
        return existing_market

    market_definition = market_payload.get('marketDefinition')
    return get_or_create_market_from_definition(market_id, market_definition)


def should_persist_market(market_payload: Dict) -> bool:
    if isinstance(market_payload.get('marketDefinition'), dict):
        return str(market_payload['marketDefinition'].get('eventTypeId')) == '2'
    market_id = market_payload.get('id')
    return find_existing_tennis_market(market_id) is not None


def save_market_snapshot_for_message(snapshot_data: Dict, market_payload: Dict) -> Optional[MarketSnapshot]:
    market = get_tennis_market(market_payload)
    if not market:
        return None

    timestamp = parse_timestamp(snapshot_data.get('pt')) or timezone.now()
    market_snapshot = MarketSnapshot.objects.create(
        market=market,
        timestamp=timestamp,
        raw_snapshot=snapshot_data,
    )

    for runner_change in market_payload.get('rc', []):
        if not isinstance(runner_change, dict):
            continue
        runner = Runner.objects.filter(market=market, runner_id=str(runner_change.get('id'))).first()
        RunnerSnapshot.objects.create(
            snapshot=market_snapshot,
            runner=runner,
            selection_id=str(runner_change.get('id', '')),
            last_price_traded=runner_change.get('ltp'),
            metadata=runner_change,
        )

    return market_snapshot


def ingest_training_archive(archive_path: str, max_files: Optional[int] = None, commit: bool = False) -> Dict[str, object]:
    total_files = 0
    tennis_files = 0
    tennis_snapshots = 0
    market_type_counts = Counter()
    event_ids = Counter()
    sample_markets = []
    created_markets = 0
    created_snapshots = 0

    for file_data in iter_snapshot_files(archive_path, max_files=max_files):
        total_files += 1
        file_contains_tennis = False

        for snapshot in parse_bz2_snapshot_file(file_data):
            for market_payload in snapshot.get('mc', []):
                if not should_persist_market(market_payload):
                    continue

                file_contains_tennis = True
                tennis_snapshots += 1

                market = get_tennis_market(market_payload)
                if market:
                    market_definition = market_payload.get('marketDefinition') or market.raw_definition or {}
                    market_type = market_definition.get('marketType', 'UNKNOWN')
                    market_type_counts[market_type] += 1
                    event_ids[str(market_definition.get('eventId', market.event.event_id))] += 1
                    if len(sample_markets) < 5:
                        sample_markets.append({
                            'eventId': market_definition.get('eventId', market.event.event_id),
                            'marketId': market.market_id,
                            'marketType': market_type,
                            'marketTime': market_definition.get('marketTime'),
                        })

                if commit:
                    with transaction.atomic():
                        snapshot_record = save_market_snapshot_for_message(snapshot, market_payload)
                        if snapshot_record is not None:
                            created_snapshots += 1
                            if snapshot_record.market is not None and snapshot_record.market.id:
                                created_markets += 0

        if file_contains_tennis:
            tennis_files += 1

    return {
        'total_files': total_files,
        'tennis_files': tennis_files,
        'tennis_snapshots': tennis_snapshots,
        'market_type_counts': market_type_counts.most_common(10),
        'event_ids': event_ids.most_common(10),
        'sample_markets': sample_markets,
        'created_snapshots': created_snapshots,
        'created_markets': created_markets,
    }

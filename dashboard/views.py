from django.shortcuts import render

from .selectors import (
    market_detail as get_market_detail,
    model_run_detail as get_model_run_detail,
    model_runs as get_model_runs,
    predictions as get_predictions,
    upcoming_markets as get_upcoming_markets,
)


def home(request):
    markets = get_upcoming_markets()
    return render(request, 'dashboard/home.html', {'markets': markets})


def market_detail(request, market_id):
    detail = get_market_detail(market_id)
    if not detail:
        return render(request, 'dashboard/market_detail.html', {'error': 'Market not found.'})
    return render(request, 'dashboard/market_detail.html', detail)


def predictions(request):
    return render(request, 'dashboard/predictions.html', {'predictions': get_predictions()})


def model_runs(request):
    return render(request, 'dashboard/model_runs.html', {'model_runs': get_model_runs()})


def model_run_detail(request, run_id):
    detail = get_model_run_detail(run_id)
    if not detail:
        return render(request, 'dashboard/model_run_detail.html', {'error': 'Model run not found.'})
    return render(request, 'dashboard/model_run_detail.html', detail)

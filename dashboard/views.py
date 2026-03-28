from django.shortcuts import render


def home(request):
    return render(request, 'dashboard/home.html')


def upcoming_markets(request):
    return render(request, 'dashboard/upcoming_markets.html')


def predictions(request):
    return render(request, 'dashboard/predictions.html')


def model_runs(request):
    return render(request, 'dashboard/model_runs.html')


def market_detail(request, market_id):
    return render(request, 'dashboard/market_detail.html', {'market_id': market_id})

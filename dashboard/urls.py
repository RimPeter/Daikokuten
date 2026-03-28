from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('upcoming/', views.upcoming_markets, name='upcoming_markets'),
    path('predictions/', views.predictions, name='predictions'),
    path('model-runs/', views.model_runs, name='model_runs'),
    path('market/<slug:market_id>/', views.market_detail, name='market_detail'),
]

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('market/<str:market_id>/', views.market_detail, name='market_detail'),
    path('predictions/', views.predictions, name='predictions'),
    path('model-runs/', views.model_runs, name='model_runs'),
    path('model-runs/<int:run_id>/', views.model_run_detail, name='model_run_detail'),
]
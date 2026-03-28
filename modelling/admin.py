from django.contrib import admin

from .models import ModelRun, Prediction


@admin.register(ModelRun)
class ModelRunAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'created_at')
    search_fields = ('name', 'version')


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('market', 'runner_id', 'predicted_probability', 'predicted_odds', 'inference_time')
    search_fields = ('runner_id', 'market__market_id')
    list_filter = ('inference_time',)

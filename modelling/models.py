from django.db import models

from markets.models import Market


class ModelRun(models.Model):
    name = models.CharField(max_length=128)
    version = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    config = models.JSONField(null=True, blank=True)
    metrics = models.JSONField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} v{self.version or 'latest'}"


class Prediction(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='predictions')
    model_run = models.ForeignKey(ModelRun, on_delete=models.SET_NULL, null=True, blank=True, related_name='predictions')
    runner_id = models.CharField(max_length=64)
    predicted_probability = models.FloatField(null=True, blank=True)
    predicted_odds = models.FloatField(null=True, blank=True)
    inference_time = models.DateTimeField(auto_now_add=True)
    raw_output = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-inference_time']

    def __str__(self):
        return f"Prediction {self.runner_id} for {self.market.market_id}"

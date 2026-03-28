from django.db import models

from markets.models import Market, MarketSnapshot


class FeatureRow(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='feature_rows')
    snapshot = models.ForeignKey(MarketSnapshot, on_delete=models.CASCADE, related_name='feature_rows')
    created_at = models.DateTimeField(auto_now_add=True)
    features = models.JSONField()
    target = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"FeatureRow {self.market.market_id} @ {self.created_at.isoformat()}"

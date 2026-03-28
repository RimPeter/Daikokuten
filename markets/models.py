from django.db import models


class Sport(models.Model):
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Event(models.Model):
    event_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sport.code} event {self.event_id}"


class Market(models.Model):
    market_id = models.CharField(max_length=64, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='markets')
    market_type = models.CharField(max_length=128, blank=True)
    market_time = models.DateTimeField(null=True, blank=True)
    suspend_time = models.DateTimeField(null=True, blank=True)
    in_play = models.BooleanField(default=False)
    raw_definition = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Market {self.market_id} ({self.market_type})"


class Runner(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='runners')
    runner_id = models.CharField(max_length=64)
    name = models.CharField(max_length=255, blank=True)
    sort_priority = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('market', 'runner_id')

    def __str__(self):
        return f"Runner {self.runner_id} ({self.name})"


class MarketSnapshot(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='snapshots')
    timestamp = models.DateTimeField()
    raw_snapshot = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Snapshot {self.market.market_id} @ {self.timestamp.isoformat()}"


class RunnerSnapshot(models.Model):
    snapshot = models.ForeignKey(MarketSnapshot, on_delete=models.CASCADE, related_name='runner_snapshots')
    runner = models.ForeignKey(Runner, on_delete=models.SET_NULL, null=True, blank=True)
    selection_id = models.CharField(max_length=64)
    last_price_traded = models.FloatField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"RunnerSnapshot {self.selection_id} @ {self.snapshot.timestamp.isoformat()}"

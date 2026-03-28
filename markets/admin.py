from django.contrib import admin
from .models import Event, Market, MarketSnapshot, Runner, RunnerSnapshot, Sport


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'sport', 'start_time')
    search_fields = ('event_id', 'name')
    list_filter = ('sport',)


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('market_id', 'event', 'market_type', 'market_time', 'in_play')
    search_fields = ('market_id', 'market_type')
    list_filter = ('market_type', 'in_play')


@admin.register(Runner)
class RunnerAdmin(admin.ModelAdmin):
    list_display = ('runner_id', 'market', 'name', 'sort_priority')
    search_fields = ('runner_id', 'name')


@admin.register(MarketSnapshot)
class MarketSnapshotAdmin(admin.ModelAdmin):
    list_display = ('market', 'timestamp', 'created_at')
    list_filter = ('market__market_type',)
    search_fields = ('market__market_id',)


@admin.register(RunnerSnapshot)
class RunnerSnapshotAdmin(admin.ModelAdmin):
    list_display = ('selection_id', 'snapshot', 'last_price_traded')
    search_fields = ('selection_id',)

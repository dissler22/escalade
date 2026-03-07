from django.contrib import admin

from .models import SessionOccurrence, SessionSeries


@admin.register(SessionSeries)
class SessionSeriesAdmin(admin.ModelAdmin):
    list_display = ("label", "weekday", "start_time", "end_time", "default_capacity", "is_active")
    list_filter = ("weekday", "is_active")
    search_fields = ("label",)


@admin.register(SessionOccurrence)
class SessionOccurrenceAdmin(admin.ModelAdmin):
    list_display = ("label", "session_date", "start_time", "capacity", "status", "is_override")
    list_filter = ("status", "is_override")
    search_fields = ("label", "notes")

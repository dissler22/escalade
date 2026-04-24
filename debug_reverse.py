import os
import django
import datetime as dt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from sessions.models import SessionSeries, SessionSeriesSlot

series = SessionSeries.objects.prefetch_related("slot_templates").first()
print("Series id:", id(series))

occ = list(series.occurrences.all().order_by("session_date"))[0]
print("Occ series id:", id(occ.series))
print("Same object?", series is occ.series)


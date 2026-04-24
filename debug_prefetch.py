import os
import django
import datetime as dt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from sessions.models import SessionSeries, SessionSeriesSlot

series = SessionSeries.objects.prefetch_related("slot_templates").first()
print("Before:", [t.start_time for t in series.slot_templates.all()])

SessionSeriesSlot.objects.create(series=series, sequence_index=1, start_time=dt.time(10, 0), end_time=dt.time(11, 0))

print("After create:", [t.start_time for t in series.slot_templates.all()])

series.refresh_from_db()
print("After refresh:", [t.start_time for t in series.slot_templates.all()])


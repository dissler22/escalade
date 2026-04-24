import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from sessions.models import SessionSeries, SessionOccurrence

series = SessionSeries.objects.first()
print(f"Series: {series.label}")
print("Templates:")
for t in series.slot_templates.all():
    print(f"  - {t.start_time} to {t.end_time}")

occ = series.occurrences.first()
print(f"\nOccurrence: {occ.label} on {occ.session_date}")
print("Slots:")
for s in occ.slots.all():
    print(f"  - {s.start_time} to {s.end_time}")


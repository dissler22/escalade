import datetime as dt

import pytest

from sessions.services import create_occurrence, create_series, update_occurrence


@pytest.mark.django_db
def test_series_occurrence_creates_slots_of_90_minutes_max(admin_user):
    occurrence = create_occurrence(
        actor=admin_user,
        cleaned_data={
            "label": "Longue séance",
            "session_date": dt.date.today() + dt.timedelta(days=10),
            "start_time": dt.time(19, 0),
            "end_time": dt.time(22, 0),
            "capacity": 16,
            "status": "open",
            "notes": "",
            "series": None,
        },
    )

    slots = list(occurrence.slots.order_by("sequence_index"))
    assert len(slots) == 2
    assert slots[0].start_time == dt.time(19, 0)
    assert slots[0].end_time == dt.time(20, 30)
    assert slots[1].start_time == dt.time(20, 30)
    assert slots[1].end_time == dt.time(22, 0)


@pytest.mark.django_db
def test_series_update_does_not_override_existing_occurrence(admin_user):
    series = create_series(
        actor=admin_user,
        cleaned_data={
            "label": "Lundi libre",
            "weekday": 0,
            "start_time": dt.time(19, 0),
            "end_time": dt.time(21, 0),
            "default_capacity": 30,
            "is_active": True,
        },
        weeks=2,
    )
    occurrence = series.occurrences.first()
    update_occurrence(actor=admin_user, occurrence=occurrence, cleaned_data={"capacity": 16}, mark_override=True)
    occurrence.refresh_from_db()
    assert occurrence.capacity == 16
    assert occurrence.slots.count() == 2

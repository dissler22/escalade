import datetime as dt

import pytest

from sessions.services import create_series, update_occurrence, update_series


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
    update_series(actor=admin_user, series=series, cleaned_data={"default_capacity": 20})
    occurrence.refresh_from_db()
    assert occurrence.capacity == 16

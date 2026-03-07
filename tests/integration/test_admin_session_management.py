import datetime as dt

import pytest
from django.urls import reverse

from sessions.models import SessionOccurrence, SessionSeries


@pytest.mark.django_db
def test_admin_can_create_series_and_occurrence(client, admin_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("sessions_admin:series-create"),
        {
            "label": "Mercredi libre",
            "weekday": SessionSeries.Weekday.WEDNESDAY,
            "start_time": "19:00",
            "end_time": "21:00",
            "default_capacity": 16,
            "is_active": "on",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert SessionSeries.objects.filter(label="Mercredi libre").exists()
    assert SessionOccurrence.objects.filter(series__label="Mercredi libre").exists()


@pytest.mark.django_db
def test_admin_can_create_one_off_occurrence(client, admin_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("sessions_admin:occurrence-create"),
        {
            "label": "Weekend libre",
            "session_date": (dt.date.today() + dt.timedelta(days=10)).isoformat(),
            "start_time": "10:00",
            "end_time": "12:00",
            "capacity": 30,
            "status": SessionOccurrence.Status.OPEN,
            "notes": "",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert SessionOccurrence.objects.filter(label="Weekend libre").exists()


@pytest.mark.django_db
def test_admin_can_change_occurrence_status(client, admin_user, open_occurrence):
    client.force_login(admin_user)
    response = client.post(
        reverse("sessions_admin:occurrence-status", args=[open_occurrence.pk]),
        {"status": SessionOccurrence.Status.CLOSED, "reason": "Salle pleine"},
        follow=True,
    )
    assert response.status_code == 200
    open_occurrence.refresh_from_db()
    assert open_occurrence.status == SessionOccurrence.Status.CLOSED

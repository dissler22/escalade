import datetime as dt

import pytest
from django.urls import reverse

from sessions.models import SessionOccurrence, SessionSeries


@pytest.mark.django_db
def test_admin_can_create_series_and_occurrence(client, admin_user):
    client.force_login(admin_user)
    landing = client.get(reverse("sessions_admin:series-list"))
    assert landing.status_code == 200
    landing_html = landing.content.decode()
    assert "Pilotage des séances" in landing_html
    assert "Administration" in landing_html

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
    html = response.content.decode()
    assert "Serie creee." in html
    assert "Séries hebdomadaires" in html
    assert SessionSeries.objects.filter(label="Mercredi libre").exists()
    assert SessionOccurrence.objects.filter(series__label="Mercredi libre").exists()


@pytest.mark.django_db
def test_admin_can_create_one_off_occurrence(client, admin_user):
    client.force_login(admin_user)
    create_page = client.get(reverse("sessions_admin:occurrence-create"))
    assert create_page.status_code == 200
    assert "Mettre à jour le statut" not in create_page.content.decode()

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
    html = response.content.decode()
    assert "Seance creee." in html
    assert "Occurrences à venir" in html
    assert SessionOccurrence.objects.filter(label="Weekend libre").exists()


@pytest.mark.django_db
def test_admin_can_change_occurrence_status(client, admin_user, open_occurrence):
    client.force_login(admin_user)
    edit_page = client.get(reverse("sessions_admin:occurrence-edit", args=[open_occurrence.pk]))
    assert edit_page.status_code == 200
    edit_html = edit_page.content.decode()
    assert "Mettre à jour le statut" in edit_html
    assert "Retour au pilotage" in edit_html

    response = client.post(
        reverse("sessions_admin:occurrence-status", args=[open_occurrence.pk]),
        {"status": SessionOccurrence.Status.CLOSED, "reason": "Salle pleine"},
        follow=True,
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert "Statut mis a jour." in html
    assert "Closed" in html
    open_occurrence.refresh_from_db()
    assert open_occurrence.status == SessionOccurrence.Status.CLOSED

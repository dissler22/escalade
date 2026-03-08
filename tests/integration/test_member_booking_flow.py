import datetime as dt

import pytest
from django.test import override_settings
from django.urls import reverse

from bookings.models import Reservation


@pytest.mark.django_db
@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver", "34.71.54.146"])
def test_member_can_book_and_cancel_flow(client, member_user, open_occurrence):
    client.force_login(member_user)
    week_start = (open_occurrence.session_date - dt.timedelta(days=open_occurrence.session_date.weekday())).isoformat()

    session_list = client.get(reverse("sessions:session-list"), HTTP_HOST="34.71.54.146")
    assert session_list.status_code == 200
    session_list_html = session_list.content.decode()
    assert "USM Viroflay Escalade" in session_list_html
    assert "Repère adhérent" in session_list_html
    assert "Planning hebdomadaire" in session_list_html
    assert "Semaine suivante" in session_list_html

    calendar_week = client.get(
        f"{reverse('sessions:session-list')}?week_start={week_start}",
        HTTP_HOST="34.71.54.146",
    )
    assert calendar_week.status_code == 200
    calendar_html = calendar_week.content.decode()
    assert open_occurrence.label in calendar_html
    assert "Détail séance" in calendar_html

    session_detail = client.get(
        reverse("sessions:session-detail", args=[open_occurrence.pk]),
        HTTP_HOST="34.71.54.146",
    )
    assert session_detail.status_code == 302
    assert f"week_start={week_start}" in session_detail.url
    assert f"selected_occurrence={open_occurrence.pk}" in session_detail.url

    detail_html = calendar_html
    assert "S'inscrire" in detail_html

    response = client.post(
        reverse("bookings:book-occurrence", args=[open_occurrence.pk]),
        {"week_start": week_start, "selected_occurrence": open_occurrence.pk},
        follow=True,
        HTTP_HOST="34.71.54.146",
    )
    assert response.status_code == 200
    booked_html = response.content.decode()
    assert "Reservation enregistree." in booked_html
    assert "Se désinscrire" in booked_html
    assert Reservation.objects.active().filter(user=member_user, occurrence=open_occurrence).exists()

    response = client.get(reverse("bookings:my-reservations"), HTTP_HOST="34.71.54.146")
    assert response.status_code == 200
    reservations_html = response.content.decode()
    assert open_occurrence.label in reservations_html
    assert "Réservation confirmée" in reservations_html

    response = client.post(
        reverse("bookings:cancel-occurrence", args=[open_occurrence.pk]),
        {"week_start": week_start, "selected_occurrence": open_occurrence.pk},
        follow=True,
        HTTP_HOST="34.71.54.146",
    )
    assert response.status_code == 200
    cancelled_html = response.content.decode()
    assert "Reservation annulee." in cancelled_html
    assert "Détail séance" in cancelled_html
    assert not Reservation.objects.active().filter(user=member_user, occurrence=open_occurrence).exists()


@pytest.mark.django_db
@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver", "34.71.54.146"])
def test_member_must_login_to_access_my_reservations_on_public_host(client):
    response = client.get(reverse("bookings:my-reservations"), HTTP_HOST="34.71.54.146")
    assert response.status_code == 302
    assert reverse("accounts:login") in response.url

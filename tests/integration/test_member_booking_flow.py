import pytest
from django.test import override_settings
from django.urls import reverse

from bookings.models import Reservation


@pytest.mark.django_db
@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver", "34.71.54.146"])
def test_member_can_book_and_cancel_flow(client, member_user, open_occurrence):
    client.force_login(member_user)

    response = client.post(
        reverse("bookings:book-occurrence", args=[open_occurrence.pk]),
        follow=True,
        HTTP_HOST="34.71.54.146",
    )
    assert response.status_code == 200
    assert Reservation.objects.active().filter(user=member_user, occurrence=open_occurrence).exists()

    response = client.get(reverse("bookings:my-reservations"), HTTP_HOST="34.71.54.146")
    assert response.status_code == 200
    assert open_occurrence.label in response.content.decode()

    response = client.post(
        reverse("bookings:cancel-occurrence", args=[open_occurrence.pk]),
        follow=True,
        HTTP_HOST="34.71.54.146",
    )
    assert response.status_code == 200
    assert not Reservation.objects.active().filter(user=member_user, occurrence=open_occurrence).exists()


@pytest.mark.django_db
@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver", "34.71.54.146"])
def test_member_must_login_to_access_my_reservations_on_public_host(client):
    response = client.get(reverse("bookings:my-reservations"), HTTP_HOST="34.71.54.146")
    assert response.status_code == 302
    assert reverse("accounts:login") in response.url

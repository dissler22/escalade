import pytest
from django.urls import reverse

from bookings.models import Reservation
from sessions.models import ResponsibleAssignment


@pytest.mark.django_db
def test_responsable_can_take_and_release_slot_without_losing_booking(
    client,
    responsable_user,
    member_user,
    open_occurrence,
    open_slot,
):
    client.force_login(responsable_user)

    response = client.post(reverse("bookings:book-occurrence", args=[open_occurrence.pk]), follow=True)
    assert response.status_code == 200
    assert Reservation.objects.active().filter(user=responsable_user, occurrence=open_occurrence).exists()

    response = client.post(reverse("sessions:take-responsibility", args=[open_slot.pk]), follow=True)
    assert response.status_code == 200
    html = response.content.decode()
    assert "Responsabilite prise sur le creneau." in html
    assert "Responsable" in html
    assert ResponsibleAssignment.objects.filter(
        slot=open_slot,
        user=responsable_user,
        status=ResponsibleAssignment.Status.ACTIVE,
    ).exists()

    response = client.post(reverse("sessions:release-responsibility", args=[open_slot.pk]), follow=True)
    assert response.status_code == 200
    assert "Responsabilite retiree sur le creneau." in response.content.decode()
    assert Reservation.objects.active().filter(user=responsable_user, occurrence=open_occurrence).exists()
    assert not ResponsibleAssignment.objects.filter(
        slot=open_slot,
        user=responsable_user,
        status=ResponsibleAssignment.Status.ACTIVE,
    ).exists()


@pytest.mark.django_db
def test_second_responsable_is_refused_in_member_flow(client, admin_user, responsable_user, open_slot):
    admin_user.grant_responsable_accreditation()
    admin_user.save()

    client.force_login(responsable_user)
    client.post(reverse("sessions:take-responsibility", args=[open_slot.pk]), follow=True)

    client.force_login(admin_user)
    response = client.post(reverse("sessions:take-responsibility", args=[open_slot.pk]), follow=True)

    assert response.status_code == 200
    assert "Ce creneau a deja un responsable." in response.content.decode()

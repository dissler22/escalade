import pytest
from django.urls import reverse

from audit.models import AuditEntry
from bookings.models import Reservation


@pytest.mark.django_db
def test_admin_can_add_and_remove_reservation(client, admin_user, member_user, open_occurrence):
    client.force_login(admin_user)

    page = client.get(reverse("bookings_admin:session-reservations", args=[open_occurrence.pk]))
    assert page.status_code == 200
    page_html = page.content.decode()
    assert "Corrections manuelles" in page_html
    assert "Ajouter un inscrit" in page_html

    response = client.post(
        reverse("bookings_admin:add-reservation", args=[open_occurrence.pk]),
        {"user_id": member_user.pk},
        follow=True,
    )
    assert response.status_code == 200
    assert "Réservation ajoutée." in response.content.decode()
    assert Reservation.objects.active().filter(user=member_user, occurrence=open_occurrence).exists()

    response = client.post(
        reverse("bookings_admin:remove-reservation", args=[open_occurrence.pk, member_user.pk]),
        follow=True,
    )
    assert response.status_code == 200
    assert "Réservation retirée." in response.content.decode()
    assert not Reservation.objects.active().filter(user=member_user, occurrence=open_occurrence).exists()

    history = client.get(reverse("audit:session-history", args=[open_occurrence.pk]))
    assert history.status_code == 200
    assert AuditEntry.objects.filter(occurrence=open_occurrence, action_type="reservation_added_manually").exists()
    assert AuditEntry.objects.filter(occurrence=open_occurrence, action_type="reservation_removed_manually").exists()

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from bookings.models import Reservation


@pytest.mark.django_db
def test_visual_refresh_member_pages_share_usmv_markers(client, member_user, open_occurrence):
    Reservation.objects.create(
        occurrence=open_occurrence,
        user=member_user,
        created_by_role="member",
    )
    client.force_login(member_user)

    pages = [
        reverse("sessions:session-list"),
        reverse("sessions:session-detail", args=[open_occurrence.pk]),
        reverse("bookings:my-reservations"),
    ]

    for path in pages:
        response = client.get(path, follow=True)
        assert response.status_code == 200
        html = response.content.decode()
        assert "USM Viroflay Escalade" in html
        assert "Repère adhérent" in html
        assert "Mes réservations" in html or "Séances" in html


@pytest.mark.django_db
def test_visual_refresh_admin_pages_share_usmv_markers(client, admin_user, member_user, open_occurrence):
    Reservation.objects.create(
        occurrence=open_occurrence,
        user=member_user,
        created_by_role="admin",
    )
    extra_member = get_user_model().objects.create_user(
        email="visual-admin-member@example.com",
        password="memberpass123",
        full_name="Visual Admin Member",
        role="member",
    )
    client.force_login(admin_user)

    pages = [
        reverse("sessions_admin:series-list"),
        reverse("sessions_admin:series-create"),
        reverse("sessions_admin:occurrence-edit", args=[open_occurrence.pk]),
        reverse("bookings_admin:session-reservations", args=[open_occurrence.pk]),
        reverse("accounts_admin:account-list"),
        reverse("audit:session-history", args=[open_occurrence.pk]),
    ]

    for path in pages:
        response = client.get(path)
        assert response.status_code == 200
        html = response.content.decode()
        assert "USM Viroflay Escalade" in html
        assert "Repère administrateur" in html

    reservations_page = client.get(reverse("bookings_admin:session-reservations", args=[open_occurrence.pk]))
    reservations_html = reservations_page.content.decode()
    assert extra_member.full_name in reservations_html or member_user.full_name in reservations_html

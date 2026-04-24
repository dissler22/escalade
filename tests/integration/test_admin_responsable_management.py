import datetime as dt

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from sessions.models import ResponsibleAssignment, SessionOccurrence
from sessions.services import take_slot_responsibility


@pytest.mark.django_db
def test_admin_can_grant_and_revoke_responsable_accreditation(client, admin_user, member_user, open_slot):
    client.force_login(admin_user)

    response = client.post(
        reverse("accounts_admin:account-status", args=[member_user.pk]),
        {
            "role": "member",
            "is_active": "true",
            "is_responsable_accredited": "true",
            "can_teach_courses": "false",
        },
        follow=True,
    )
    assert response.status_code == 200
    member_user.refresh_from_db()
    assert member_user.is_responsable_accredited is True

    take_slot_responsibility(user=member_user, slot=open_slot)
    response = client.post(
        reverse("accounts_admin:account-status", args=[member_user.pk]),
        {
            "role": "member",
            "is_active": "true",
            "is_responsable_accredited": "false",
            "can_teach_courses": "false",
        },
        follow=True,
    )
    assert response.status_code == 200
    member_user.refresh_from_db()
    assert member_user.is_responsable_accredited is False
    assert not ResponsibleAssignment.objects.filter(
        slot=open_slot,
        user=member_user,
        status=ResponsibleAssignment.Status.ACTIVE,
    ).exists()


@pytest.mark.django_db
def test_admin_can_create_long_session_and_assign_responsable(client, admin_user, responsable_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("sessions_admin:occurrence-create"),
        {
            "label": "Grande pratique libre",
            "session_date": (dt.date.today() + dt.timedelta(days=10)).isoformat(),
            "start_time": "18:00",
            "end_time": "21:00",
            "capacity": 20,
            "status": SessionOccurrence.Status.OPEN,
            "notes": "",
        },
        follow=True,
    )
    assert response.status_code == 200
    occurrence = SessionOccurrence.objects.get(label="Grande pratique libre")
    assert occurrence.slots.count() == 2

    slot = occurrence.slots.order_by("sequence_index").first()
    response = client.post(
        reverse("sessions_admin:slot-assign-responsable", args=[slot.pk]),
        {"user_id": responsable_user.pk},
        follow=True,
    )
    assert response.status_code == 200
    slot.refresh_from_db()
    assert slot.current_responsable == responsable_user

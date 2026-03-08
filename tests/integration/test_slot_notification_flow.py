import datetime as dt

import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from bookings.services import create_member_booking
from sessions.models import EmailAutomationSettings, SessionSlot
from sessions.services import process_slot_coverage_deadlines


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    NOTIFICATION_SENDER_EMAIL="escalade.usmv@gmail.com",
)
def test_admin_sees_sender_and_j2_auto_cancel_notifies_member(
    client,
    admin_user,
    member_user,
    open_occurrence,
    open_slot,
):
    open_occurrence.session_date = dt.date.today() + dt.timedelta(days=2)
    open_occurrence.save(update_fields=["session_date"])
    other_slot = open_occurrence.slots.exclude(pk=open_slot.pk).first()
    other_slot.status = SessionSlot.Status.OPEN
    other_slot.save(update_fields=["status"])
    client.force_login(admin_user)
    client.post(
        reverse("sessions_admin:slot-assign-responsable", args=[other_slot.pk]),
        {"user_id": admin_user.pk},
        follow=True,
    )
    create_member_booking(user=member_user, occurrence=open_occurrence)

    account_page = client.get(reverse("accounts_admin:account-list"))
    assert account_page.status_code == 200
    assert "escalade.usmv@gmail.com" in account_page.content.decode()

    client.post(
        reverse("accounts_admin:email-automation"),
        {
            "reminder_days_before": 4,
            "cancellation_days_before": 2,
            "reminder_email_subject": "Rappel {session_label}",
            "reminder_email_body": "Rappel personnalisé {slot_start}",
            "cancellation_email_subject": "Annulation personnalisée {session_label}",
            "cancellation_email_body": "Annulation personnalisée {slot_start}-{slot_end}",
        },
        follow=True,
    )

    summary = process_slot_coverage_deadlines(today=dt.date.today())

    open_slot.refresh_from_db()
    assert summary["slots_auto_cancelled"] == 1
    assert open_slot.status == SessionSlot.Status.CANCELLED
    assert len(mail.outbox) == 1
    assert member_user.email in mail.outbox[0].to
    assert mail.outbox[0].subject == f"Annulation personnalisée {open_occurrence.label}"
    assert "Annulation personnalisée" in mail.outbox[0].body

import datetime as dt

import pytest
from django.core import mail
from django.test import override_settings

from sessions.models import SessionSlot
from sessions.services import process_slot_coverage_deadlines


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    NOTIFICATION_SENDER_EMAIL="escalade.usmv@gmail.com",
)
def test_j7_reminder_is_sent_to_responsables(admin_user, responsable_user, open_slot):
    open_slot.occurrence.session_date = dt.date.today() + dt.timedelta(days=7)
    open_slot.occurrence.save(update_fields=["session_date"])
    other_slot = open_slot.occurrence.slots.exclude(pk=open_slot.pk).first()
    other_slot.status = SessionSlot.Status.CANCELLED
    other_slot.save(update_fields=["status"])

    summary = process_slot_coverage_deadlines(today=dt.date.today())

    assert summary["reminders_sent"] == 2
    assert len(mail.outbox) == 1
    assert responsable_user.email in mail.outbox[0].to
    assert admin_user.email in mail.outbox[0].to


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    NOTIFICATION_SENDER_EMAIL="escalade.usmv@gmail.com",
)
def test_j2_uncovered_slot_is_cancelled_and_notified(member_user, open_slot):
    open_slot.occurrence.session_date = dt.date.today() + dt.timedelta(days=2)
    open_slot.occurrence.save(update_fields=["session_date"])
    other_slot = open_slot.occurrence.slots.exclude(pk=open_slot.pk).first()
    other_slot.status = SessionSlot.Status.CANCELLED
    other_slot.save(update_fields=["status"])
    open_slot.occurrence.reservations.create(user=member_user, created_by_role="member")

    summary = process_slot_coverage_deadlines(today=dt.date.today())

    open_slot.refresh_from_db()
    assert summary["slots_auto_cancelled"] == 1
    assert summary["cancellation_notices_sent"] == 1
    assert open_slot.status == SessionSlot.Status.CANCELLED
    assert len(mail.outbox) == 1
    assert member_user.email in mail.outbox[0].to

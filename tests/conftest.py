import datetime as dt

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

from sessions.models import SessionOccurrence, SessionSlot


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_user(
        email="admin@example.com",
        password="adminpass123",
        full_name="Admin User",
        role="admin",
    )


@pytest.fixture
def member_user(db):
    return get_user_model().objects.create_user(
        email="member@example.com",
        password="memberpass123",
        full_name="Member User",
        role="member",
    )


@pytest.fixture
def member_user_2(db):
    return get_user_model().objects.create_user(
        email="member2@example.com",
        password="memberpass123",
        full_name="Member Two",
        role="member",
    )


@pytest.fixture
def responsable_user(db):
    user = get_user_model().objects.create_user(
        email="responsable@example.com",
        password="memberpass123",
        full_name="Responsable User",
        role="member",
    )
    user.grant_responsable_accreditation()
    user.save()
    return user


@pytest.fixture
def open_occurrence(admin_user, db):
    occurrence = SessionOccurrence.objects.create(
        label="Lundi libre",
        session_date=timezone.localdate() + dt.timedelta(days=7),
        start_time=dt.time(19, 0),
        end_time=dt.time(21, 0),
        capacity=2,
        status=SessionOccurrence.Status.OPEN,
        created_by=admin_user,
    )
    SessionSlot.objects.create(
        occurrence=occurrence,
        sequence_index=1,
        start_time=dt.time(19, 0),
        end_time=dt.time(20, 30),
        capacity=2,
        status=SessionSlot.Status.OPEN,
    )
    SessionSlot.objects.create(
        occurrence=occurrence,
        sequence_index=2,
        start_time=dt.time(20, 30),
        end_time=dt.time(21, 0),
        capacity=2,
        status=SessionSlot.Status.OPEN,
    )
    return occurrence


@pytest.fixture
def open_slot(open_occurrence):
    return open_occurrence.slots.order_by("sequence_index").first()

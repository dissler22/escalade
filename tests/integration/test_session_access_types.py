import datetime as dt

import pytest
from django.urls import reverse
from django.utils import timezone

from sessions.models import CourseEnrollment, SessionOccurrence
from sessions.models import SessionSeries, SessionSlot


@pytest.mark.django_db
def test_admin_can_manage_orange_passport_and_course_memberships(
    client,
    admin_user,
    plain_member_user,
    course_series,
):
    client.force_login(admin_user)

    response = client.post(
        reverse("accounts_admin:account-status", args=[plain_member_user.pk]),
        {
            "role": "member",
            "is_active": "true",
            "is_responsable_accredited": "false",
            "has_orange_passport": "true",
            "course_series_ids": [str(course_series.pk)],
        },
        follow=True,
    )

    assert response.status_code == 200
    plain_member_user.refresh_from_db()
    assert plain_member_user.has_orange_passport is True
    assert CourseEnrollment.objects.active().filter(user=plain_member_user, series=course_series).exists()


@pytest.mark.django_db
def test_calendar_distinguishes_free_practice_and_course(
    client,
    course_member,
    open_occurrence,
    course_occurrence,
):
    client.force_login(course_member)
    week_start = (open_occurrence.session_date - dt.timedelta(days=open_occurrence.session_date.weekday())).isoformat()

    response = client.get(
        f"{reverse('sessions:session-list')}?week_start={week_start}&selected_occurrence={course_occurrence.pk}"
    )

    assert response.status_code == 200
    html = response.content.decode()
    assert "Pratique libre" in html
    assert "Cours" in html
    assert "Prof: Teacher User" in html
    assert "sans logique référent" in html


@pytest.mark.django_db
def test_calendar_uses_series_label_when_free_practice_occurrence_label_is_generic(
    client,
    admin_user,
    member_user,
):
    series = SessionSeries.objects.create(
        label="Mardi soir",
        weekday=1,
        start_time=dt.time(19, 0),
        end_time=dt.time(21, 0),
        default_capacity=12,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        created_by=admin_user,
    )
    occurrence = SessionOccurrence.objects.create(
        series=series,
        label="Pratique libre",
        session_date=timezone.localdate() + dt.timedelta(days=7),
        start_time=dt.time(19, 0),
        end_time=dt.time(21, 0),
        capacity=12,
        session_type=SessionSeries.SessionType.FREE_PRACTICE,
        status=SessionOccurrence.Status.OPEN,
        created_by=admin_user,
    )
    SessionSlot.objects.create(
        occurrence=occurrence,
        sequence_index=1,
        start_time=dt.time(19, 0),
        end_time=dt.time(20, 30),
        capacity=12,
        status="open",
    )

    client.force_login(member_user)
    week_start = (occurrence.session_date - dt.timedelta(days=occurrence.session_date.weekday())).isoformat()

    response = client.get(
        f"{reverse('sessions:session-list')}?week_start={week_start}&selected_occurrence={occurrence.pk}"
    )

    assert response.status_code == 200
    html = response.content.decode()
    assert "Mardi soir" in html
    assert 'title="Seance (19:00 - 21:00)"' not in html


@pytest.mark.django_db
def test_teacher_can_edit_only_own_course_occurrence(client, teacher_user, course_occurrence, admin_user):
    client.force_login(teacher_user)

    response = client.post(
        reverse("sessions:teacher-occurrence-edit", args=[course_occurrence.pk]),
        {
            "label": "Cours adultes avancé",
            "session_date": course_occurrence.session_date.isoformat(),
            "start_time": course_occurrence.start_time.strftime("%H:%M"),
            "end_time": course_occurrence.end_time.strftime("%H:%M"),
            "capacity": course_occurrence.capacity,
            "status": SessionOccurrence.Status.OPEN,
            "notes": "Prévoir corde et baudrier",
        },
        follow=True,
    )

    assert response.status_code == 200
    course_occurrence.refresh_from_db()
    assert course_occurrence.label == "Cours adultes avancé"
    assert course_occurrence.notes == "Prévoir corde et baudrier"

    other_teacher = admin_user
    course_occurrence.teacher = other_teacher
    course_occurrence.save(update_fields=["teacher"])
    response = client.get(reverse("sessions:teacher-occurrence-edit", args=[course_occurrence.pk]))
    assert response.status_code == 404

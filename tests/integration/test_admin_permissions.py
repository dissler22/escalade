import pytest
from django.urls import reverse

from django.contrib.auth import get_user_model
from accounts.identity import TEMPORARY_ACCESS_CODE
from sessions.models import CourseEnrollment, EmailAutomationSettings, SessionSeries


@pytest.mark.django_db
def test_member_cannot_open_account_admin(client, member_user):
    client.force_login(member_user)
    response = client.get(reverse("accounts_admin:account-list"))
    assert response.status_code == 302
    response = client.get(reverse("accounts_admin:email-automation"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_admin_can_open_account_admin(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse("accounts_admin:account-list"))
    assert response.status_code == 200
    html = response.content.decode()
    assert "Gestion des droits" in html
    assert "Comptes du club" in html
    assert "Créer un accès club" in html

    response = client.get(reverse("accounts_admin:email-automation"))
    assert response.status_code == 200
    html = response.content.decode()
    assert "Jours avant la séance" in html
    assert "Variables disponibles" in html


@pytest.mark.django_db
def test_admin_can_disable_account(client, admin_user, member_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("accounts_admin:account-status", args=[member_user.pk]),
        {"role": "member", "is_active": "false", "can_teach_courses": "false"},
        follow=True,
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert "Compte mis à jour." in html
    assert "inactif" in html
    updated_user = get_user_model().objects.get(pk=member_user.pk)
    assert updated_user.is_active is False


@pytest.mark.django_db
def test_admin_can_update_email_automation_settings(client, admin_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("accounts_admin:email-automation"),
        {
            "reminder_days_before": 5,
            "cancellation_days_before": 1,
            "reminder_email_subject": "Rappel {session_label}",
            "reminder_email_body": "Corps rappel {slot_start}",
            "cancellation_email_subject": "Annulation {session_label}",
            "cancellation_email_body": "Corps annulation {slot_end}",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "Automatisation des mails mise à jour." in response.content.decode()
    automation_settings = EmailAutomationSettings.objects.get(pk=1)
    assert automation_settings.reminder_days_before == 5
    assert automation_settings.cancellation_days_before == 1


@pytest.mark.django_db
def test_admin_can_create_account_with_temporary_password_and_course(client, admin_user, course_series):
    client.force_login(admin_user)

    response = client.post(
        reverse("accounts_admin:account-create"),
        {
            "full_name": "Claire Test",
            "email": "",
            "role": "member",
            "is_responsable_accredited": "false",
            "has_orange_passport": "true",
            "can_teach_courses": "true",
            "is_active": "true",
            "course_series_ids": [str(course_series.pk)],
        },
        follow=True,
    )

    assert response.status_code == 200
    created_user = get_user_model().objects.get(full_name="Claire Test")
    assert created_user.password_state == created_user.PasswordState.TEMPORARY
    assert created_user.has_orange_passport is True
    assert created_user.can_teach_courses is True
    assert created_user.email is None
    assert created_user.check_password(TEMPORARY_ACCESS_CODE)
    assert CourseEnrollment.objects.active().filter(user=created_user, series=course_series).exists()
    assert "Code temporaire" in response.content.decode()


@pytest.mark.django_db
def test_teacher_select_only_lists_users_with_teaching_capability(client, admin_user, plain_member_user):
    client.force_login(admin_user)
    teaching_user = get_user_model().objects.create_user(
        email="coach@example.com",
        password="coachpass123",
        full_name="Coach User",
        role="member",
        can_teach_courses=True,
    )

    response = client.get(reverse("sessions_admin:series-create"))

    assert response.status_code == 200
    html = response.content.decode()
    assert teaching_user.full_name in html
    assert plain_member_user.full_name not in html


@pytest.mark.django_db
def test_admin_can_reset_account_password(client, admin_user, member_user):
    client.force_login(admin_user)

    response = client.post(
        reverse("accounts_admin:account-reset-password", args=[member_user.pk]),
        follow=True,
    )

    assert response.status_code == 200
    member_user.refresh_from_db()
    assert member_user.password_state == member_user.PasswordState.RESET_REQUIRED
    assert member_user.check_password(TEMPORARY_ACCESS_CODE)
    assert "Nouveau code temporaire" in response.content.decode()


@pytest.mark.django_db
def test_admin_can_import_accounts_from_tsv(client, admin_user):
    client.force_login(admin_user)
    beginner_series = SessionSeries.objects.create(
        label="Adultes débutants mardi",
        weekday=1,
        start_time="19:00",
        end_time="21:00",
        default_capacity=20,
        session_type=SessionSeries.SessionType.COURSE,
        created_by=admin_user,
    )
    practice_series = SessionSeries.objects.create(
        label="Adultes pratiquants vendredi",
        weekday=4,
        start_time="19:00",
        end_time="21:00",
        default_capacity=20,
        session_type=SessionSeries.SessionType.COURSE,
        created_by=admin_user,
    )
    existing_user = get_user_model().objects.create_user(
        email="old@example.com",
        password="anciencode123",
        full_name="Adrien Breuillier",
        role="member",
    )

    response = client.post(
        reverse("accounts_admin:account-import"),
        {
            "roster_data": (
                "Prénom\tNom\tCréneau\tCommentaire\tPasseport orange\tRéférent salle\n"
                "Adrien\tBarny\tAdultes débutants mardi\tSécurité orange\toui\t\n"
                "Adrien\tBreuillier\tAdultes pratiquants vendredi\t\t\toui\n"
            )
        },
        follow=True,
    )

    assert response.status_code == 200
    created_user = get_user_model().objects.get(full_name="Adrien Barny")
    existing_user.refresh_from_db()

    assert created_user.password_state == created_user.PasswordState.TEMPORARY
    assert created_user.check_password(TEMPORARY_ACCESS_CODE)
    assert created_user.has_orange_passport is True
    assert CourseEnrollment.objects.active().filter(user=created_user, series=beginner_series).exists()

    assert existing_user.is_responsable_accredited is True
    assert CourseEnrollment.objects.active().filter(user=existing_user, series=practice_series).exists()
    assert "Import terminé" in response.content.decode()

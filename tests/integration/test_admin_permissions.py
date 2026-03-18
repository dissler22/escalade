import pytest
from django.urls import reverse

from django.contrib.auth import get_user_model
from sessions.models import CourseEnrollment, EmailAutomationSettings


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
    assert "Automatisation des mails" in html
    assert "Placeholders disponibles" in html


@pytest.mark.django_db
def test_admin_can_disable_account(client, admin_user, member_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("accounts_admin:account-status", args=[member_user.pk]),
        {"role": "member", "is_active": "false"},
        follow=True,
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert "Compte mis a jour." in html
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
    assert "Automatisation des mails mise a jour." in response.content.decode()
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
            "email": "claire@example.com",
            "role": "member",
            "is_responsable_accredited": "false",
            "has_orange_passport": "true",
            "is_active": "true",
            "course_series_ids": [str(course_series.pk)],
        },
        follow=True,
    )

    assert response.status_code == 200
    created_user = get_user_model().objects.get(email="claire@example.com")
    assert created_user.password_state == created_user.PasswordState.TEMPORARY
    assert created_user.has_orange_passport is True
    assert CourseEnrollment.objects.active().filter(user=created_user, series=course_series).exists()
    assert "Code temporaire" in response.content.decode()


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
    assert "Nouveau code temporaire" in response.content.decode()

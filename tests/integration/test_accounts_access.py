import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import override_settings


@pytest.mark.django_db
def test_member_must_login_to_access_sessions(client):
    response = client.get(reverse("sessions:session-list"))
    assert response.status_code == 302
    assert reverse("accounts:login") in response.url


@pytest.mark.django_db
def test_inactive_user_cannot_login(client, member_user):
    member_user.is_active = False
    member_user.save()
    response = client.post(
        reverse("accounts:login"),
        {"email": member_user.email, "password": "memberpass123"},
        follow=True,
    )
    assert "Identifiants invalides" in response.content.decode()


@pytest.mark.django_db
def test_member_cannot_access_admin_pages(client, member_user):
    client.force_login(member_user)
    response = client.get(reverse("sessions_admin:series-list"))
    assert response.status_code == 302


@pytest.mark.django_db
@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver", "34.71.54.146"])
def test_public_entry_redirects_to_login_on_public_host(client):
    response = client.get(reverse("accounts:home"), HTTP_HOST="34.71.54.146")
    assert response.status_code == 302
    assert response.url == reverse("accounts:login")


@pytest.mark.django_db
@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver", "34.71.54.146"])
def test_member_can_log_in_from_public_entry_and_reach_sessions(client, member_user, open_occurrence):
    login_page = client.get(reverse("accounts:login"), HTTP_HOST="34.71.54.146")
    assert login_page.status_code == 200
    login_html = login_page.content.decode()
    assert "USM Viroflay Escalade" in login_html
    assert "Entrer avec votre compte club" in login_html

    response = client.post(
        reverse("accounts:login"),
        {"email": member_user.email, "password": "memberpass123"},
        follow=True,
        HTTP_HOST="34.71.54.146",
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert "Repère adhérent" in html
    assert "Séances ouvertes" in html
    assert "Planning hebdomadaire" in html


@pytest.mark.django_db
def test_temporary_password_forces_password_change_flow(client):
    user = get_user_model().objects.create_user(
        email="temp-user@example.com",
        password="tempcode123",
        full_name="Temp User",
        role="member",
        password_state="temporary",
    )

    response = client.post(
        reverse("accounts:login"),
        {"email": user.email, "password": "tempcode123"},
        follow=True,
    )

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("accounts:password-change")
    assert "Code temporaire detecte" in response.content.decode()

    response = client.post(
        reverse("accounts:password-change"),
        {
            "old_password": "tempcode123",
            "new_password1": "nouveau-code-456",
            "new_password2": "nouveau-code-456",
        },
        follow=True,
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.password_state == user.PasswordState.ACTIVE
    assert response.request["PATH_INFO"] == reverse("sessions:session-list")

import pytest
from django.urls import reverse


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

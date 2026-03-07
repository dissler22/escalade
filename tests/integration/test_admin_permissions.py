import pytest
from django.urls import reverse

from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_member_cannot_open_account_admin(client, member_user):
    client.force_login(member_user)
    response = client.get(reverse("accounts_admin:account-list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_admin_can_open_account_admin(client, admin_user):
    client.force_login(admin_user)
    response = client.get(reverse("accounts_admin:account-list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_can_disable_account(client, admin_user, member_user):
    client.force_login(admin_user)
    response = client.post(
        reverse("accounts_admin:account-status", args=[member_user.pk]),
        {"role": "member", "is_active": "false"},
        follow=True,
    )
    assert response.status_code == 200
    updated_user = get_user_model().objects.get(pk=member_user.pk)
    assert updated_user.is_active is False

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .identity import build_login_key_from_parts, build_lookup_key


class NameAuthenticationBackend(ModelBackend):
    def authenticate(
        self,
        request,
        username=None,
        password=None,
        first_name=None,
        last_name=None,
        **kwargs,
    ):
        if not password:
            return None

        login_key = ""
        if first_name or last_name:
            login_key = build_login_key_from_parts(first_name, last_name)
        elif username:
            login_key = build_lookup_key(username)
        if not login_key:
            return None

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(login_key=login_key)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

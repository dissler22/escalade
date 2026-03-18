from django.shortcuts import redirect
from django.urls import resolve


class PasswordStateEnforcementMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and user.password_state != user.PasswordState.ACTIVE
        ):
            resolver_match = resolve(request.path_info)
            namespace = resolver_match.namespace
            url_name = resolver_match.url_name
            if not (namespace == "accounts" and url_name in {"password-change", "logout"}):
                return redirect("accounts:password-change")
        return self.get_response(request)

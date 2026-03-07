from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import record_event


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.role == "admin")(view_func))


@admin_required
def account_list(request: HttpRequest) -> HttpResponse:
    users = get_user_model().objects.order_by("full_name", "email")
    return render(request, "admin/accounts/account_list.html", {"users": users})


@admin_required
def update_account_status(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(get_user_model(), pk=user_id)
    if request.method == "POST":
        user.is_active = request.POST.get("is_active") == "true"
        role = request.POST.get("role")
        if role in {"member", "admin"}:
            user.role = role
        user.save()
        record_event(
            actor=request.user,
            action_type="account_updated",
            target_type="account",
            target_id=user.pk,
            reason="admin status update",
            metadata={"is_active": user.is_active, "role": user.role},
        )
        messages.success(request, "Compte mis a jour.")
    return redirect("accounts_admin:account-list")

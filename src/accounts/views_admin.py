from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from audit.services import record_event
from sessions.forms import EmailAutomationSettingsForm
from sessions.services import (
    get_email_automation_settings,
    get_notification_sender_summary,
    revoke_future_responsable_assignments,
)


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_admin_role)(view_func))


@admin_required
def account_list(request: HttpRequest) -> HttpResponse:
    users = get_user_model().objects.order_by("full_name", "email")
    return render(
        request,
        "admin/accounts/account_list.html",
        {
            "users": users,
            "notification_sender": get_notification_sender_summary(),
        },
    )


@admin_required
def update_account_status(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(get_user_model(), pk=user_id)
    if request.method == "POST":
        previous_accreditation = user.is_responsable_accredited
        user.is_active = request.POST.get("is_active") == "true"
        role = request.POST.get("role")
        if role in {"member", "admin"}:
            user.role = role
        wants_responsable = request.POST.get("is_responsable_accredited") == "true"
        if wants_responsable and not user.is_responsable_accredited:
            user.grant_responsable_accreditation(actor=request.user)
        elif not wants_responsable and user.is_responsable_accredited:
            user.revoke_responsable_accreditation()
        user.save()

        record_event(
            actor=request.user,
            action_type="account_updated",
            target_type="account",
            target_id=user.pk,
            reason="admin status update",
            metadata={
                "is_active": user.is_active,
                "role": user.role,
                "is_responsable_accredited": user.is_responsable_accredited,
            },
        )
        if not previous_accreditation and user.is_responsable_accredited:
            record_event(
                actor=request.user,
                action_type="responsable_accreditation_granted",
                target_type="account",
                target_id=user.pk,
                metadata={"email": user.email},
            )
        if previous_accreditation and not user.is_responsable_accredited:
            revoked_count = revoke_future_responsable_assignments(actor=request.user, user=user)
            record_event(
                actor=request.user,
                action_type="responsable_accreditation_revoked",
                target_type="account",
                target_id=user.pk,
                metadata={"email": user.email, "revoked_assignments": revoked_count},
            )
        messages.success(request, "Compte mis a jour.")
    return redirect("accounts_admin:account-list")


@admin_required
def email_automation(request: HttpRequest) -> HttpResponse:
    automation_settings = get_email_automation_settings()
    form = EmailAutomationSettingsForm(request.POST or None, instance=automation_settings)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Automatisation des mails mise a jour.")
        return redirect("accounts_admin:email-automation")
    return render(
        request,
        "admin/accounts/email_automation.html",
        {
            "form": form,
            "notification_sender": get_notification_sender_summary(),
        },
    )

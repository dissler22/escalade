from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from audit.services import record_event
from accounts.forms import AdminAccountCreateForm, BulkAccountImportForm
from accounts.identity import TEMPORARY_ACCESS_CODE
from accounts.importers import import_accounts_from_roster
from sessions.forms import EmailAutomationSettingsForm
from sessions.models import CourseEnrollment, SessionSeries
from sessions.services import (
    get_email_automation_settings,
    get_notification_sender_summary,
    revoke_future_responsable_assignments,
)


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_admin_role)(view_func))


def _sync_active_course_enrollments(*, actor, user, valid_course_ids):
    previous_course_ids = set(
        CourseEnrollment.objects.active().filter(user=user).values_list("series_id", flat=True)
    )

    for series_id in sorted(valid_course_ids - previous_course_ids):
        enrollment = CourseEnrollment.objects.create(
            user=user,
            series_id=series_id,
            assigned_by=actor,
        )
        record_event(
            actor=actor,
            action_type="course_enrollment_assigned",
            target_type="course_enrollment",
            target_id=enrollment.pk,
            metadata={"user_id": user.pk, "series_id": series_id},
        )

    if previous_course_ids - valid_course_ids:
        enrollments = CourseEnrollment.objects.active().filter(
            user=user,
            series_id__in=previous_course_ids - valid_course_ids,
        )
        for enrollment in enrollments:
            enrollment.status = CourseEnrollment.Status.REMOVED
            enrollment.removed_at = timezone.now()
            enrollment.removed_by = actor
            enrollment.save(update_fields=["status", "removed_at", "removed_by"])
            record_event(
                actor=actor,
                action_type="course_enrollment_removed",
                target_type="course_enrollment",
                target_id=enrollment.pk,
                metadata={"user_id": user.pk, "series_id": enrollment.series_id},
            )

    return previous_course_ids


def _build_account_list_context(*, create_form=None, import_form=None):
    User = get_user_model()
    course_series = SessionSeries.objects.filter(session_type=SessionSeries.SessionType.COURSE).order_by("label")
    users = User.objects.prefetch_related(
        "course_enrollments__series",
        "reservations__occurrence__series",
    ).order_by("full_name", "email")
    course_memberships = {
        user.pk: {
            enrollment.series_id
            for enrollment in user.course_enrollments.all()
            if enrollment.status == CourseEnrollment.Status.ACTIVE
        }
        for user in users
    }
    account_rows = []
    for user in users:
        count = 0
        for reservation in user.reservations.filter(status="active").select_related("occurrence", "occurrence__series"):
            occurrence = reservation.occurrence
            if occurrence is None:
                continue
            if occurrence.is_free_practice and not user.can_book_free_practice:
                count += 1
            if occurrence.is_course and occurrence.series_id not in course_memberships[user.pk]:
                count += 1
        account_rows.append(
            {
                "user": user,
                "course_ids": course_memberships[user.pk],
                "recovery_count": count,
                "is_teacher": user.can_teach_courses,
            }
        )
    return {
        "users": users,
        "account_rows": account_rows,
        "course_series": course_series,
        "create_form": create_form or AdminAccountCreateForm(),
        "import_form": import_form or BulkAccountImportForm(),
        "notification_sender": get_notification_sender_summary(),
    }


@admin_required
def account_list(request: HttpRequest) -> HttpResponse:
    return render(request, "admin/accounts/account_list.html", _build_account_list_context())


@admin_required
def create_account(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return redirect("accounts_admin:account-list")

    form = AdminAccountCreateForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "admin/accounts/account_list.html",
            _build_account_list_context(create_form=form),
            status=400,
        )

    cleaned_data = form.cleaned_data
    with transaction.atomic():
        user = get_user_model().objects.create_user(
            email=cleaned_data["email"],
            password=TEMPORARY_ACCESS_CODE,
            full_name=cleaned_data["full_name"],
            role=cleaned_data["role"],
            is_active=cleaned_data["is_active"],
            password_state=get_user_model().PasswordState.TEMPORARY,
        )
        if cleaned_data["is_responsable_accredited"]:
            user.grant_responsable_accreditation(actor=request.user)
        if cleaned_data["has_orange_passport"]:
            user.grant_orange_passport(actor=request.user)
        user.can_teach_courses = cleaned_data["can_teach_courses"]
        user.save()

        for series in cleaned_data["course_series_ids"]:
            enrollment = CourseEnrollment.objects.create(
                user=user,
                series=series,
                assigned_by=request.user,
            )
            record_event(
                actor=request.user,
                action_type="course_enrollment_assigned",
                target_type="course_enrollment",
                target_id=enrollment.pk,
                metadata={"user_id": user.pk, "series_id": series.pk},
            )

    record_event(
        actor=request.user,
        action_type="account_created",
        target_type="account",
        target_id=user.pk,
        reason="admin account creation",
        metadata={
            "email": user.email,
            "role": user.role,
            "is_responsable_accredited": user.is_responsable_accredited,
            "has_orange_passport": user.has_orange_passport,
            "can_teach_courses": user.can_teach_courses,
            "course_series_ids": [series.pk for series in cleaned_data["course_series_ids"]],
            "password_state": user.password_state,
        },
    )
    messages.success(
        request,
        f"Compte créé pour {user.full_name}. Code temporaire : {TEMPORARY_ACCESS_CODE}",
    )
    return redirect("accounts_admin:account-list")


@admin_required
def import_accounts(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return redirect("accounts_admin:account-list")

    form = BulkAccountImportForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "admin/accounts/account_list.html",
            _build_account_list_context(import_form=form),
            status=400,
        )

    try:
        result = import_accounts_from_roster(
            actor=request.user,
            roster_data=form.cleaned_data["roster_data"],
        )
    except ValidationError as exc:
        form.add_error("roster_data", exc)
        return render(
            request,
            "admin/accounts/account_list.html",
            _build_account_list_context(import_form=form),
            status=400,
        )

    messages.success(
        request,
        f"Import terminé: {result.created_count} compte(s) créé(s), {result.updated_count} compte(s) mis à jour. Code temporaire par défaut: {TEMPORARY_ACCESS_CODE}.",
    )
    return redirect("accounts_admin:account-list")


@admin_required
def update_account_status(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(get_user_model(), pk=user_id)
    if request.method == "POST":
        previous_accreditation = user.is_responsable_accredited
        previous_orange_passport = user.has_orange_passport
        previous_can_teach_courses = user.can_teach_courses
        selected_course_ids = {
            int(series_id)
            for series_id in request.POST.getlist("course_series_ids")
            if str(series_id).isdigit()
        }
        valid_course_ids = set(
            SessionSeries.objects.filter(
                pk__in=selected_course_ids,
                session_type=SessionSeries.SessionType.COURSE,
            ).values_list("pk", flat=True)
        )

        with transaction.atomic():
            user.is_active = request.POST.get("is_active") == "true"
            role = request.POST.get("role")
            if role in {"member", "admin"}:
                user.role = role
            wants_responsable = request.POST.get("is_responsable_accredited") == "true"
            if wants_responsable and not user.is_responsable_accredited:
                user.grant_responsable_accreditation(actor=request.user)
            elif not wants_responsable and user.is_responsable_accredited:
                user.revoke_responsable_accreditation()

            wants_orange_passport = request.POST.get("has_orange_passport") == "true"
            if wants_orange_passport and not user.has_orange_passport:
                user.grant_orange_passport(actor=request.user)
            elif not wants_orange_passport and user.has_orange_passport:
                user.revoke_orange_passport()
            user.can_teach_courses = request.POST.get("can_teach_courses") == "true"
            user.save()

            _sync_active_course_enrollments(
                actor=request.user,
                user=user,
                valid_course_ids=valid_course_ids,
            )

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
                "has_orange_passport": user.has_orange_passport,
                "can_teach_courses": user.can_teach_courses,
                "course_series_ids": sorted(valid_course_ids),
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
        if not previous_orange_passport and user.has_orange_passport:
            record_event(
                actor=request.user,
                action_type="orange_passport_granted",
                target_type="account",
                target_id=user.pk,
                metadata={"email": user.email},
            )
        if previous_orange_passport and not user.has_orange_passport:
            record_event(
                actor=request.user,
                action_type="orange_passport_revoked",
                target_type="account",
                target_id=user.pk,
                metadata={"email": user.email},
            )
        if previous_can_teach_courses != user.can_teach_courses:
            record_event(
                actor=request.user,
                action_type="teaching_capability_updated",
                target_type="account",
                target_id=user.pk,
                metadata={"email": user.email, "can_teach_courses": user.can_teach_courses},
            )
        messages.success(request, "Compte mis à jour.")
    return redirect("accounts_admin:account-list")


@admin_required
def reset_account_password(request: HttpRequest, user_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect("accounts_admin:account-list")

    user = get_object_or_404(get_user_model(), pk=user_id)
    user.set_temporary_password(TEMPORARY_ACCESS_CODE, state=user.PasswordState.RESET_REQUIRED)
    user.save(update_fields=["password", "password_state", "updated_at"])
    record_event(
        actor=request.user,
        action_type="account_password_reset",
        target_type="account",
        target_id=user.pk,
        reason="admin password reset",
        metadata={"email": user.email, "password_state": user.password_state},
    )
    messages.success(
        request,
        f"Nouveau code temporaire pour {user.full_name}: {TEMPORARY_ACCESS_CODE}",
    )
    return redirect("accounts_admin:account-list")


@admin_required
def email_automation(request: HttpRequest) -> HttpResponse:
    automation_settings = get_email_automation_settings()
    form = EmailAutomationSettingsForm(request.POST or None, instance=automation_settings)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Automatisation des mails mise à jour.")
        return redirect("accounts_admin:email-automation")
    return render(
        request,
        "admin/accounts/email_automation.html",
        {
            "form": form,
            "notification_sender": get_notification_sender_summary(),
        },
    )

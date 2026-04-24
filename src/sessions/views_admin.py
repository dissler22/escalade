import datetime as dt

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import SessionOccurrenceForm, SessionSeriesForm, SessionSeriesSlotFormSet
from .models import SessionOccurrence, SessionSeries, SessionSlot
from .services import (
    _future_occurrence_filter,
    assign_slot_responsibility,
    change_occurrence_status,
    change_slot_status,
    create_occurrence,
    create_series,
    delete_slot,
    get_notification_sender_summary,
    occurrence_is_past,
    release_slot_responsibility,
    slot_is_past,
    update_occurrence,
    update_series,
    update_slot,
)


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_admin_role)(view_func))


def _redirect_with_fallback(request: HttpRequest, default_url: str) -> HttpResponse:
    return_to = request.POST.get("return_to", "").strip()
    return redirect(return_to or default_url)


def _parse_time_value(value, fallback):
    if not value:
        return fallback
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return value
    return dt.time.fromisoformat(str(value))


@admin_required
def series_list(request: HttpRequest) -> HttpResponse:
    User = get_user_model()
    series_items = (
        SessionSeries.objects.select_related("default_teacher")
        .prefetch_related("occurrences__reservations", "occurrences__slots__responsable_assignments")
        .order_by("label", "weekday")
    )
    series_rows = [
        {"series": item, "delete_confirmation": _build_series_delete_confirmation(item)}
        for item in series_items
    ]
    occurrences = (
        SessionOccurrence.objects.prefetch_related(
            "reservations__user",
            "slots__reservations",
            "slots__responsable_assignments__user",
        )
        .select_related("series", "teacher", "series__default_teacher")
        .filter(_future_occurrence_filter())
        .order_by("session_date", "start_time")[:30]
    )
    occurrence_rows = [
        {"occurrence": occurrence, "delete_confirmation": _build_occurrence_delete_confirmation(occurrence)}
        for occurrence in occurrences
    ]
    responsable_candidates = User.objects.filter(is_active=True).order_by("full_name")
    return render(
        request,
        "admin/sessions/series_list.html",
        {
            "series_rows": series_rows,
            "occurrence_rows": occurrence_rows,
            "responsable_candidates": responsable_candidates,
            "notification_sender": get_notification_sender_summary(),
        },
    )


def _can_delete_occurrence(occurrence):
    has_reservations = occurrence.reservations.active().exists()
    has_assignments = occurrence.slots.filter(
        responsable_assignments__status="active"
    ).exists()
    return not has_reservations and not has_assignments


def _ensure_occurrence_not_past(occurrence) -> str | None:
    if occurrence_is_past(occurrence=occurrence, now=timezone.now()):
        return "Les occurrences passées sont en lecture seule."
    return None


def _ensure_slot_not_past(slot) -> str | None:
    if slot_is_past(slot=slot, now=timezone.now()):
        return "Les créneaux passés sont en lecture seule."
    return None


def _build_occurrence_delete_confirmation(occurrence):
    attendee_names = list(
        occurrence.reservations.active()
        .select_related("user")
        .order_by("user__full_name", "id")
        .values_list("user__full_name", flat=True)
    )
    responsable_names = list(
        occurrence.slots.filter(responsable_assignments__status="active")
        .select_related("responsable_assignments__user")
        .order_by("start_time", "sequence_index", "responsable_assignments__user__full_name")
        .values_list("responsable_assignments__user__full_name", flat=True)
        .distinct()
    )

    lines = [
        f"Supprimer définitivement la séance \"{occurrence.label}\" du {occurrence.session_date:%d/%m/%Y} ?",
    ]
    if attendee_names:
        lines.append("")
        lines.append("Inscrits actifs :")
        lines.extend(f"- {name}" for name in attendee_names)
    if responsable_names:
        lines.append("")
        lines.append("Responsables affectés :")
        lines.extend(f"- {name}" for name in responsable_names)
    if attendee_names or responsable_names:
        lines.append("")
        lines.append("Cette suppression retirera aussi ces inscriptions et affectations.")
    return "\n".join(lines)


def _build_series_delete_confirmation(series):
    lines = [f"Supprimer définitivement la série \"{series.label}\" ?"]
    impacted_occurrences = []
    for occurrence in series.occurrences.all():
        attendee_count = occurrence.reservations.active().count()
        responsable_count = occurrence.slots.filter(responsable_assignments__status="active").count()
        if attendee_count or responsable_count:
            impacted_occurrences.append(
                (occurrence.session_date, occurrence.label, attendee_count, responsable_count)
            )

    if impacted_occurrences:
        lines.append("")
        lines.append("Séances impactées :")
        for session_date, label, attendee_count, responsable_count in impacted_occurrences:
            lines.append(
                f"- {session_date:%d/%m/%Y} · {label} · {attendee_count} inscrit(s) · {responsable_count} responsable(s)"
            )
        lines.append("")
        lines.append("Cette suppression retirera aussi les séances, inscriptions et affectations liées.")
    return "\n".join(lines)


@admin_required
def series_create(request: HttpRequest) -> HttpResponse:
    form = SessionSeriesForm(request.POST or None)
    slot_formset = SessionSeriesSlotFormSet(request.POST or None)
    
    if request.method == "POST" and form.is_valid() and slot_formset.is_valid():
        create_series(actor=request.user, cleaned_data=form.cleaned_data, slot_formset=slot_formset)
        messages.success(request, "Série créée.")
        return redirect("sessions_admin:series-list")
        
    return render(
        request, 
        "admin/sessions/series_form.html", 
        {
            "form": form, 
            "slot_formset": slot_formset,
            "title": "Nouvelle série"
        }
    )


@admin_required
def series_edit(request: HttpRequest, series_id: int) -> HttpResponse:
    series = get_object_or_404(
        SessionSeries.objects.prefetch_related(
            "occurrences__reservations",
            "occurrences__slots__reservations",
            "occurrences__slots__responsable_assignments__user",
            "slot_templates",
        ),
        pk=series_id,
    )
    form = SessionSeriesForm(request.POST or None, instance=series)
    slot_formset = SessionSeriesSlotFormSet(request.POST or None, instance=series)
    
    if request.method == "POST" and form.is_valid() and slot_formset.is_valid():
        update_series(actor=request.user, series=series, cleaned_data=form.cleaned_data, slot_formset=slot_formset)
        messages.success(request, "Série mise à jour.")
        return redirect("sessions_admin:series-list")
        
    User = get_user_model()
    responsable_candidates = User.objects.filter(is_active=True).order_by("full_name")
    return render(
        request,
        "admin/sessions/series_form.html",
        {
            "form": form,
            "slot_formset": slot_formset,
            "title": "Modifier la série",
            "series": series,
            "series_delete_confirmation": _build_series_delete_confirmation(series),
            "responsable_candidates": responsable_candidates,
            "series_return_to": reverse("sessions_admin:series-edit", args=[series.pk]),
        },
    )


@admin_required
def occurrence_create(request: HttpRequest) -> HttpResponse:
    form = SessionOccurrenceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_occurrence(actor=request.user, cleaned_data=form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, "Séance créée.")
            return redirect("sessions_admin:series-list")
    return render(request, "admin/sessions/occurrence_form.html", {"form": form, "title": "Nouvelle séance"})


@admin_required
def occurrence_edit(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(
        SessionOccurrence.objects.prefetch_related(
            "reservations__user",
            "slots__reservations",
            "slots__responsable_assignments__user",
        )
        .select_related("series", "teacher", "series__default_teacher"),
        pk=occurrence_id,
    )
    form = SessionOccurrenceForm(request.POST or None, instance=occurrence)
    if request.method == "POST" and form.is_valid():
        past_error = _ensure_occurrence_not_past(occurrence)
        if past_error:
            messages.error(request, past_error)
            return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence.pk)
        try:
            update_occurrence(
                actor=request.user,
                occurrence=occurrence,
                cleaned_data=form.cleaned_data,
                mark_override=bool(occurrence.series),
            )
        except ValidationError as exc:
            form.add_error(None, exc.message)
        else:
            messages.success(request, "Séance mise à jour.")
            return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence.pk)
    User = get_user_model()
    responsable_candidates = User.objects.filter(is_active=True).order_by("full_name")
    return render(
        request,
        "admin/sessions/occurrence_form.html",
        {
            "form": form,
            "title": "Modifier la séance",
            "occurrence": occurrence,
            "is_course": occurrence.is_course,
            "responsable_candidates": responsable_candidates,
            "occurrence_delete_confirmation": _build_occurrence_delete_confirmation(occurrence),
        },
    )


@admin_required
def occurrence_status(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence, pk=occurrence_id)
    return_to = request.POST.get("return_to") if request.method == "POST" else ""
    if request.method == "POST":
        past_error = _ensure_occurrence_not_past(occurrence)
        if past_error:
            messages.error(request, past_error)
            return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence.pk)
        status = request.POST.get("status", "")
        reason = request.POST.get("reason", "")
        try:
            change_occurrence_status(actor=request.user, occurrence=occurrence, status=status, reason=reason)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Statut mis à jour.")
    if return_to == "list":
        return redirect(f"{reverse('sessions_admin:series-list')}?panel=occurrences")
    return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence.pk)


@admin_required
def series_delete(request: HttpRequest, series_id: int) -> HttpResponse:
    series = get_object_or_404(
        SessionSeries.objects.prefetch_related("occurrences__slots", "occurrences__reservations"),
        pk=series_id,
    )
    if request.method == "POST":
        series.occurrences.all().delete()
        series.delete()
        messages.success(request, "Série supprimée.")
    return redirect("sessions_admin:series-list")


@admin_required
def occurrence_delete(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence.objects.prefetch_related("slots"), pk=occurrence_id)
    if request.method == "POST":
        past_error = _ensure_occurrence_not_past(occurrence)
        if past_error:
            messages.error(request, past_error)
            return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence_id)
        occurrence.delete()
        messages.success(request, "Séance supprimée.")
        return redirect(f"{reverse('sessions_admin:series-list')}?panel=occurrences")
    return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence_id)


@admin_required
def slot_update_view(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "Les cours n utilisent pas de creneaux responsables.")
        return _redirect_with_fallback(
            request,
            reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
        )
    if request.method == "POST":
        past_error = _ensure_slot_not_past(slot)
        if past_error:
            messages.error(request, past_error)
            return _redirect_with_fallback(
                request,
                reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
            )
        try:
            update_slot(
                actor=request.user,
                slot=slot,
                cleaned_data={
                    "start_time": _parse_time_value(request.POST.get("start_time"), slot.start_time),
                    "end_time": _parse_time_value(request.POST.get("end_time"), slot.end_time),
                    "capacity": int(request.POST.get("capacity", slot.capacity)),
                    "status": request.POST.get("status") or slot.status,
                },
            )
        except (ValidationError, ValueError) as exc:
            messages.error(request, getattr(exc, "message", str(exc)))
        else:
            messages.success(request, "Créneau mis à jour.")
    return _redirect_with_fallback(
        request,
        reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
    )


@admin_required
def slot_status(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "Les cours n utilisent pas de creneaux responsables.")
        return _redirect_with_fallback(
            request,
            reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
        )
    if request.method == "POST":
        past_error = _ensure_slot_not_past(slot)
        if past_error:
            messages.error(request, past_error)
            return _redirect_with_fallback(
                request,
                reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
            )
        status = request.POST.get("status", "")
        reason = request.POST.get("reason", "")
        try:
            change_slot_status(actor=request.user, slot=slot, status=status, reason=reason)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Statut du créneau mis à jour.")
    return _redirect_with_fallback(
        request,
        reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
    )


@admin_required
def slot_delete_view(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "Les cours n utilisent pas de creneaux responsables.")
        return _redirect_with_fallback(
            request,
            reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
        )
    if request.method == "POST":
        past_error = _ensure_slot_not_past(slot)
        if past_error:
            messages.error(request, past_error)
            return _redirect_with_fallback(
                request,
                reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
            )
        delete_slot(actor=request.user, slot=slot)
        messages.success(request, "Créneau supprimé.")
    return _redirect_with_fallback(
        request,
        reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
    )


@admin_required
def slot_assign_responsable(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "La couverture referent est reservee aux pratiques libres.")
        return _redirect_with_fallback(
            request,
            reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
        )
    if request.method == "POST":
        past_error = _ensure_slot_not_past(slot)
        if past_error:
            messages.error(request, past_error)
            return _redirect_with_fallback(
                request,
                reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
            )
        user = get_object_or_404(get_user_model(), pk=request.POST.get("user_id"))
        try:
            assign_slot_responsibility(actor=request.user, slot=slot, user=user)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Responsable affecté.")
    return _redirect_with_fallback(
        request,
        reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
    )


@admin_required
def slot_release_responsable(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "La couverture referent est reservee aux pratiques libres.")
        return _redirect_with_fallback(
            request,
            reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
        )
    if request.method == "POST":
        past_error = _ensure_slot_not_past(slot)
        if past_error:
            messages.error(request, past_error)
            return _redirect_with_fallback(
                request,
                reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
            )
        try:
            release_slot_responsibility(
                actor=request.user,
                slot=slot,
                user=slot.current_responsable,
                reason="admin_manual_release",
            )
        except ValidationError as exc:
            messages.error(request, exc.message)
        except Exception as exc:  # noqa: BLE001
            messages.error(request, str(exc))
        else:
            messages.success(request, "Responsable retiré.")
    return _redirect_with_fallback(
        request,
        reverse("sessions_admin:occurrence-edit", args=[slot.occurrence_id]),
    )

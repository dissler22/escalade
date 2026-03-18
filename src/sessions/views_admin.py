from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SessionOccurrenceForm, SessionSeriesForm
from .models import SessionOccurrence, SessionSeries, SessionSlot
from .services import (
    assign_slot_responsibility,
    change_occurrence_status,
    change_slot_status,
    create_occurrence,
    create_series,
    get_notification_sender_summary,
    release_slot_responsibility,
    update_occurrence,
    update_series,
    update_slot,
)


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_admin_role)(view_func))


@admin_required
def series_list(request: HttpRequest) -> HttpResponse:
    User = get_user_model()
    series_items = SessionSeries.objects.select_related("default_teacher").order_by("label", "weekday")
    occurrences = (
        SessionOccurrence.objects.prefetch_related(
            "slots__reservations",
            "slots__responsable_assignments__user",
        )
        .select_related("series", "teacher", "series__default_teacher")
        .order_by("session_date", "start_time")[:30]
    )
    responsable_candidates = User.objects.filter(is_active=True).exclude(email="").order_by("full_name")
    return render(
        request,
        "admin/sessions/series_list.html",
        {
            "series_items": series_items,
            "occurrences": occurrences,
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


@admin_required
def series_create(request: HttpRequest) -> HttpResponse:
    form = SessionSeriesForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        create_series(actor=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, "Serie creee.")
        return redirect("sessions_admin:series-list")
    return render(request, "admin/sessions/series_form.html", {"form": form, "title": "Nouvelle serie"})


@admin_required
def series_edit(request: HttpRequest, series_id: int) -> HttpResponse:
    series = get_object_or_404(SessionSeries, pk=series_id)
    form = SessionSeriesForm(request.POST or None, instance=series)
    if request.method == "POST" and form.is_valid():
        update_series(actor=request.user, series=series, cleaned_data=form.cleaned_data)
        messages.success(request, "Serie mise a jour.")
        return redirect("sessions_admin:series-list")
    return render(
        request,
        "admin/sessions/series_form.html",
        {
            "form": form,
            "title": "Modifier la serie",
            "series": series,
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
            messages.success(request, "Seance creee.")
            return redirect("sessions_admin:series-list")
    return render(request, "admin/sessions/occurrence_form.html", {"form": form, "title": "Nouvelle seance"})


@admin_required
def occurrence_edit(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(
        SessionOccurrence.objects.prefetch_related("slots__reservations", "slots__responsable_assignments__user")
        .select_related("series", "teacher", "series__default_teacher"),
        pk=occurrence_id,
    )
    form = SessionOccurrenceForm(request.POST or None, instance=occurrence)
    if request.method == "POST" and form.is_valid():
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
            messages.success(request, "Seance mise a jour.")
            return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence.pk)
    User = get_user_model()
    responsable_candidates = User.objects.filter(is_active=True).order_by("full_name")
    return render(
        request,
        "admin/sessions/occurrence_form.html",
        {
            "form": form,
            "title": "Modifier la seance",
            "occurrence": occurrence,
            "is_course": occurrence.is_course,
            "responsable_candidates": responsable_candidates,
        },
    )


@admin_required
def occurrence_status(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence, pk=occurrence_id)
    if request.method == "POST":
        status = request.POST.get("status", "")
        reason = request.POST.get("reason", "")
        try:
            change_occurrence_status(actor=request.user, occurrence=occurrence, status=status, reason=reason)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Statut mis a jour.")
    return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence.pk)


@admin_required
def series_delete(request: HttpRequest, series_id: int) -> HttpResponse:
    series = get_object_or_404(SessionSeries.objects.prefetch_related("occurrences__slots"), pk=series_id)
    if request.method == "POST":
        blocking_occurrence = next((occ for occ in series.occurrences.all() if not _can_delete_occurrence(occ)), None)
        if blocking_occurrence is not None:
            messages.error(request, "Impossible de supprimer cette serie car une seance a deja des inscrits ou un responsable.")
        else:
            series.delete()
            messages.success(request, "Serie supprimee.")
    return redirect("sessions_admin:series-list")


@admin_required
def occurrence_delete(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence.objects.prefetch_related("slots"), pk=occurrence_id)
    if request.method == "POST":
        if not _can_delete_occurrence(occurrence):
            messages.error(request, "Impossible de supprimer cette seance car elle a deja des inscrits ou un responsable.")
        else:
            occurrence.delete()
            messages.success(request, "Seance supprimee.")
            return redirect("sessions_admin:series-list")
    return redirect("sessions_admin:occurrence-edit", occurrence_id=occurrence_id)


@admin_required
def slot_update_view(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "Les cours n utilisent pas de creneaux responsables.")
        return redirect("sessions_admin:occurrence-edit", occurrence_id=slot.occurrence_id)
    if request.method == "POST":
        try:
            update_slot(
                actor=request.user,
                slot=slot,
                cleaned_data={
                    "start_time": request.POST.get("start_time") or slot.start_time,
                    "end_time": request.POST.get("end_time") or slot.end_time,
                    "capacity": int(request.POST.get("capacity", slot.capacity)),
                    "status": request.POST.get("status") or slot.status,
                },
            )
        except (ValidationError, ValueError) as exc:
            messages.error(request, getattr(exc, "message", str(exc)))
        else:
            messages.success(request, "Creneau mis a jour.")
    return redirect("sessions_admin:occurrence-edit", occurrence_id=slot.occurrence_id)


@admin_required
def slot_status(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "Les cours n utilisent pas de creneaux responsables.")
        return redirect("sessions_admin:occurrence-edit", occurrence_id=slot.occurrence_id)
    if request.method == "POST":
        status = request.POST.get("status", "")
        reason = request.POST.get("reason", "")
        try:
            change_slot_status(actor=request.user, slot=slot, status=status, reason=reason)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Statut du creneau mis a jour.")
    return redirect("sessions_admin:occurrence-edit", occurrence_id=slot.occurrence_id)


@admin_required
def slot_assign_responsable(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "La couverture referent est reservee aux pratiques libres.")
        return redirect("sessions_admin:occurrence-edit", occurrence_id=slot.occurrence_id)
    if request.method == "POST":
        user = get_object_or_404(get_user_model(), pk=request.POST.get("user_id"))
        try:
            assign_slot_responsibility(actor=request.user, slot=slot, user=user)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Responsable affecte.")
    return redirect("sessions_admin:occurrence-edit", occurrence_id=slot.occurrence_id)


@admin_required
def slot_release_responsable(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if slot.occurrence.is_course:
        messages.error(request, "La couverture referent est reservee aux pratiques libres.")
        return redirect("sessions_admin:occurrence-edit", occurrence_id=slot.occurrence_id)
    if request.method == "POST":
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
            messages.success(request, "Responsable retire.")
    return redirect("sessions_admin:occurrence-edit", occurrence_id=slot.occurrence_id)

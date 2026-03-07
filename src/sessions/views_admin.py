from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SessionOccurrenceForm, SessionSeriesForm
from .models import SessionOccurrence, SessionSeries
from .services import (
    change_occurrence_status,
    create_occurrence,
    create_series,
    update_occurrence,
    update_series,
)


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.role == "admin")(view_func))


@admin_required
def series_list(request: HttpRequest) -> HttpResponse:
    series_items = SessionSeries.objects.order_by("label", "weekday")
    occurrences = SessionOccurrence.objects.select_related("series").order_by("session_date", "start_time")[:30]
    return render(
        request,
        "admin/sessions/series_list.html",
        {"series_items": series_items, "occurrences": occurrences},
    )


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
    return render(request, "admin/sessions/series_form.html", {"form": form, "title": "Modifier la serie"})


@admin_required
def occurrence_create(request: HttpRequest) -> HttpResponse:
    form = SessionOccurrenceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        create_occurrence(actor=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, "Seance creee.")
        return redirect("sessions_admin:series-list")
    return render(request, "admin/sessions/occurrence_form.html", {"form": form, "title": "Nouvelle seance"})


@admin_required
def occurrence_edit(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence, pk=occurrence_id)
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
            return redirect("sessions_admin:series-list")
    return render(request, "admin/sessions/occurrence_form.html", {"form": form, "title": "Modifier la seance"})


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
    return redirect("sessions_admin:series-list")

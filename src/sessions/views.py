from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import ResponsibleAssignment, SessionOccurrence, SessionSlot
from .services import (
    build_member_calendar_page,
    build_member_calendar_url,
    release_slot_responsibility,
    resolve_calendar_return_context,
    take_slot_responsibility,
)


def _redirect_to_calendar(request: HttpRequest, *, occurrence: SessionOccurrence, anchor: str = "session-detail") -> HttpResponse:
    context = resolve_calendar_return_context(
        week_start_value=request.POST.get("week_start") or request.GET.get("week_start"),
        selected_occurrence_value=request.POST.get("selected_occurrence") or request.GET.get("selected_occurrence"),
        occurrence=occurrence,
    )
    return redirect(
        build_member_calendar_url(
            week_start=context["week_start"],
            selected_occurrence=context["selected_occurrence"],
            anchor=anchor,
        )
    )


@login_required
def session_list(request: HttpRequest) -> HttpResponse:
    calendar_page = build_member_calendar_page(
        user=request.user,
        week_start_value=request.GET.get("week_start"),
        selected_occurrence_value=request.GET.get("selected_occurrence"),
    )
    return render(
        request,
        "sessions/session_list.html",
        {
            "calendar_page": calendar_page,
            "week": calendar_page.week,
            "selected_detail": calendar_page.selected_detail,
        },
    )


@login_required
def session_detail(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(
        SessionOccurrence.objects.prefetch_related(
            "slots__reservations",
            "slots__responsable_assignments__user",
        ),
        pk=occurrence_id,
    )
    if occurrence.ends_at > timezone.now():
        return redirect(build_member_calendar_url(occurrence=occurrence, anchor="session-detail"))
    if occurrence.status == SessionOccurrence.Status.CANCELLED and not request.user.is_admin_role:
        raise Http404()
    return render(
        request,
        "sessions/session_detail.html",
        {
            "occurrence": occurrence,
            "calendar_url": build_member_calendar_url(),
        },
    )


@login_required
def take_responsibility(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if request.method == "POST":
        try:
            take_slot_responsibility(user=request.user, slot=slot)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Responsabilite prise sur le creneau.")
    return _redirect_to_calendar(request, occurrence=slot.occurrence)


@login_required
def release_responsibility(request: HttpRequest, slot_id: int) -> HttpResponse:
    slot = get_object_or_404(SessionSlot.objects.select_related("occurrence"), pk=slot_id)
    if request.method == "POST":
        try:
            release_slot_responsibility(actor=request.user, slot=slot)
        except ResponsibleAssignment.DoesNotExist:
            messages.error(request, "Responsabilite introuvable.")
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Responsabilite retiree sur le creneau.")
    return _redirect_to_calendar(request, occurrence=slot.occurrence)

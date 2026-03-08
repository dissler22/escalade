from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from sessions.models import SessionOccurrence
from sessions.services import (
    build_member_calendar_url,
    get_occurrence_week_start,
    list_member_reservations,
    resolve_calendar_return_context,
)

from .models import Reservation
from .services import cancel_member_booking, create_member_booking


def _redirect_after_occurrence_action(
    request: HttpRequest,
    *,
    occurrence: SessionOccurrence,
    fallback_to_reservations: bool = False,
) -> HttpResponse:
    has_calendar_context = any(
        value
        for value in (
            request.POST.get("week_start"),
            request.POST.get("selected_occurrence"),
            request.GET.get("week_start"),
            request.GET.get("selected_occurrence"),
        )
    )
    if not has_calendar_context and fallback_to_reservations:
        return redirect("bookings:my-reservations")
    context = resolve_calendar_return_context(
        week_start_value=request.POST.get("week_start") or request.GET.get("week_start"),
        selected_occurrence_value=request.POST.get("selected_occurrence") or request.GET.get("selected_occurrence"),
        occurrence=occurrence,
    )
    return redirect(
        build_member_calendar_url(
            week_start=context["week_start"],
            selected_occurrence=context["selected_occurrence"],
            anchor="session-detail",
        )
    )


@login_required
def book_occurrence(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence, pk=occurrence_id)
    if request.method == "POST":
        try:
            create_member_booking(user=request.user, occurrence=occurrence)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Reservation enregistree.")
    return _redirect_after_occurrence_action(request, occurrence=occurrence)


@login_required
def cancel_occurrence(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence, pk=occurrence_id)
    if request.method == "POST":
        try:
            cancel_member_booking(user=request.user, occurrence=occurrence)
        except Reservation.DoesNotExist:
            messages.error(request, "Reservation introuvable.")
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Reservation annulee.")
    return _redirect_after_occurrence_action(
        request,
        occurrence=occurrence,
        fallback_to_reservations=True,
    )


@login_required
def my_reservations(request: HttpRequest) -> HttpResponse:
    reservations = list_member_reservations(request.user)
    reservation_cards = [
        {
            "reservation": reservation,
            "calendar_url": build_member_calendar_url(
                week_start=get_occurrence_week_start(reservation.occurrence),
                selected_occurrence=reservation.occurrence_id,
                anchor="session-detail",
            ),
            "week_start_iso": get_occurrence_week_start(reservation.occurrence).isoformat(),
        }
        for reservation in reservations
    ]
    return render(
        request,
        "bookings/my_reservations.html",
        {
            "reservation_cards": reservation_cards,
        },
    )

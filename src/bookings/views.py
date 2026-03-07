from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Reservation
from sessions.models import SessionOccurrence
from sessions.services import list_member_reservations
from .services import cancel_member_booking, create_member_booking


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
    return redirect("sessions:session-detail", occurrence_id=occurrence.pk)


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
    return redirect("bookings:my-reservations")


@login_required
def my_reservations(request: HttpRequest) -> HttpResponse:
    reservations = list_member_reservations(request.user)
    return render(request, "bookings/my_reservations.html", {"reservations": reservations})

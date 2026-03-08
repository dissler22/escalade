from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from sessions.models import SessionOccurrence

from .models import Reservation
from .services import add_manual_booking, remove_manual_booking


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_admin_role)(view_func))


@admin_required
def session_reservations(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence.objects.prefetch_related("reservations__user"), pk=occurrence_id)
    members = get_user_model().objects.filter(is_active=True).order_by("full_name")
    return render(
        request,
        "admin/bookings/session_reservations.html",
        {
            "occurrence": occurrence,
            "members": members,
            "reservations": list(occurrence.reservations.active().select_related("user")),
        },
    )


@admin_required
def add_reservation(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence, pk=occurrence_id)
    if request.method == "POST":
        user = get_object_or_404(get_user_model(), pk=request.POST.get("user_id"))
        try:
            add_manual_booking(actor=request.user, occurrence=occurrence, user=user)
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Reservation ajoutee.")
    return redirect("bookings_admin:session-reservations", occurrence_id=occurrence.pk)


@admin_required
def remove_reservation(request: HttpRequest, occurrence_id: int, user_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence, pk=occurrence_id)
    user = get_object_or_404(get_user_model(), pk=user_id)
    if request.method == "POST":
        try:
            remove_manual_booking(actor=request.user, occurrence=occurrence, user=user)
        except Reservation.DoesNotExist:
            messages.error(request, "Reservation introuvable.")
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Reservation retiree.")
    return redirect("bookings_admin:session-reservations", occurrence_id=occurrence.pk)

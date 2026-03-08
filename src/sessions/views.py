from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import ResponsibleAssignment, SessionOccurrence, SessionSlot
from .services import list_member_open_occurrences, take_slot_responsibility, release_slot_responsibility


@login_required
def session_list(request: HttpRequest) -> HttpResponse:
    occurrences = list_member_open_occurrences()
    return render(request, "sessions/session_list.html", {"occurrences": occurrences})


@login_required
def session_detail(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(
        SessionOccurrence.objects.prefetch_related(
            "slots__reservations",
            "slots__responsable_assignments__user",
        ),
        pk=occurrence_id,
    )
    if occurrence.status == SessionOccurrence.Status.CANCELLED and not request.user.is_admin_role:
        raise Http404()

    my_reservation = request.user.reservations.active().filter(occurrence=occurrence).first()
    my_assignments = {
        assignment.slot_id: assignment
        for assignment in request.user.responsable_assignments.filter(
            slot__occurrence=occurrence,
            status=ResponsibleAssignment.Status.ACTIVE,
        )
    }
    slot_cards = [
        {
            "slot": slot,
            "my_assignment": my_assignments.get(slot.id),
        }
        for slot in occurrence.slots.all()
    ]
    return render(
        request,
        "sessions/session_detail.html",
        {
            "occurrence": occurrence,
            "my_reservation": my_reservation,
            "slot_cards": slot_cards,
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
    return redirect("sessions:session-detail", occurrence_id=slot.occurrence_id)


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
    return redirect("sessions:session-detail", occurrence_id=slot.occurrence_id)

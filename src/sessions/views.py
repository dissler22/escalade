from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .services import list_member_open_occurrences


@login_required
def session_list(request: HttpRequest) -> HttpResponse:
    occurrences = list_member_open_occurrences()
    return render(request, "sessions/session_list.html", {"occurrences": occurrences})


@login_required
def session_detail(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = None
    my_reservation = None
    occurrences = list_member_open_occurrences()
    occurrence = occurrences.filter(pk=occurrence_id).first()
    if occurrence is None:
        my_reservation = request.user.reservations.active().select_related("occurrence").filter(
            occurrence_id=occurrence_id
        ).first()
        if my_reservation:
            occurrence = my_reservation.occurrence
    if occurrence is None:
        from django.http import Http404

        raise Http404()
    if my_reservation is None:
        my_reservation = request.user.reservations.active().filter(occurrence=occurrence).first()
    return render(
        request,
        "sessions/session_detail.html",
        {"occurrence": occurrence, "my_reservation": my_reservation},
    )

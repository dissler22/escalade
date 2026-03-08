from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from sessions.models import SessionOccurrence

from .services import get_occurrence_history


def admin_required(view_func):
    return login_required(user_passes_test(lambda user: user.is_admin_role)(view_func))


@admin_required
def session_history(request: HttpRequest, occurrence_id: int) -> HttpResponse:
    occurrence = get_object_or_404(SessionOccurrence, pk=occurrence_id)
    history = get_occurrence_history(occurrence)
    return render(
        request,
        "admin/audit/session_history.html",
        {"occurrence": occurrence, "history": history},
    )

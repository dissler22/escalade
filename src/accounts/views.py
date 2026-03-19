from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import NameAuthenticationForm, RequiredPasswordChangeForm


def home(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("sessions:session-list")
    return redirect("accounts:login")


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        if request.user.password_state != request.user.PasswordState.ACTIVE:
            return redirect("accounts:password-change")
        return redirect("sessions:session-list")

    form = NameAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.password_state != user.PasswordState.ACTIVE:
            messages.warning(
                request,
                "Code temporaire detecte. Renseignez votre email et choisissez maintenant votre code personnel.",
            )
            return redirect("accounts:password-change")
        messages.success(request, "Connexion reussie.")
        return redirect("sessions:session-list")
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, "Deconnexion reussie.")
    return redirect("accounts:login")


@login_required
@never_cache
def password_change_view(request: HttpRequest) -> HttpResponse:
    if request.user.password_state == request.user.PasswordState.ACTIVE:
        return redirect("sessions:session-list")

    form = RequiredPasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.mark_password_active()
        user.save(update_fields=["email", "password", "password_state", "updated_at"])
        update_session_auth_hash(request, user)
        messages.success(request, "Email et code mis a jour.")
        return redirect("sessions:session-list")
    return render(request, "accounts/password_change.html", {"form": form})

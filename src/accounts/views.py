from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import EmailAuthenticationForm


def home(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("sessions:session-list")
    return redirect("accounts:login")


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("sessions:session-list")

    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Connexion reussie.")
        return redirect("sessions:session-list")
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, "Deconnexion reussie.")
    return redirect("accounts:login")

from django.urls import path

from . import views


app_name = "audit"

urlpatterns = [
    path("sessions/<int:occurrence_id>/", views.session_history, name="session-history"),
]

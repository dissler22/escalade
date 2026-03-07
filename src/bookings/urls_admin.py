from django.urls import path

from . import views_admin


app_name = "bookings_admin"

urlpatterns = [
    path("sessions/<int:occurrence_id>/", views_admin.session_reservations, name="session-reservations"),
    path("sessions/<int:occurrence_id>/add/", views_admin.add_reservation, name="add-reservation"),
    path(
        "sessions/<int:occurrence_id>/remove/<int:user_id>/",
        views_admin.remove_reservation,
        name="remove-reservation",
    ),
]

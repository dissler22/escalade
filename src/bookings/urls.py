from django.urls import path

from . import views


app_name = "bookings"

urlpatterns = [
    path("mine/", views.my_reservations, name="my-reservations"),
    path("<int:occurrence_id>/reserve/", views.book_occurrence, name="book-occurrence"),
    path("<int:occurrence_id>/cancel/", views.cancel_occurrence, name="cancel-occurrence"),
]

from django.urls import path

from . import views


app_name = "sessions"

urlpatterns = [
    path("", views.session_list, name="session-list"),
    path("<int:occurrence_id>/", views.session_detail, name="session-detail"),
    path("teaching/<int:occurrence_id>/edit/", views.teacher_occurrence_edit, name="teacher-occurrence-edit"),
    path("slots/<int:slot_id>/responsibility/take/", views.take_responsibility, name="take-responsibility"),
    path("slots/<int:slot_id>/responsibility/release/", views.release_responsibility, name="release-responsibility"),
]

from django.urls import path

from . import views


app_name = "sessions"

urlpatterns = [
    path("", views.session_list, name="session-list"),
    path("<int:occurrence_id>/", views.session_detail, name="session-detail"),
]

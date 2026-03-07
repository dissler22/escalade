from django.urls import path

from . import views_admin


app_name = "sessions_admin"

urlpatterns = [
    path("", views_admin.series_list, name="series-list"),
    path("series/new/", views_admin.series_create, name="series-create"),
    path("series/<int:series_id>/edit/", views_admin.series_edit, name="series-edit"),
    path("occurrences/new/", views_admin.occurrence_create, name="occurrence-create"),
    path("occurrences/<int:occurrence_id>/edit/", views_admin.occurrence_edit, name="occurrence-edit"),
    path("occurrences/<int:occurrence_id>/status/", views_admin.occurrence_status, name="occurrence-status"),
]

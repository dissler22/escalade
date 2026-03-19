from django.urls import path

from . import views_admin


app_name = "sessions_admin"

urlpatterns = [
    path("", views_admin.series_list, name="series-list"),
    path("series/new/", views_admin.series_create, name="series-create"),
    path("series/<int:series_id>/edit/", views_admin.series_edit, name="series-edit"),
    path("series/<int:series_id>/delete/", views_admin.series_delete, name="series-delete"),
    path("occurrences/new/", views_admin.occurrence_create, name="occurrence-create"),
    path("occurrences/<int:occurrence_id>/edit/", views_admin.occurrence_edit, name="occurrence-edit"),
    path("occurrences/<int:occurrence_id>/status/", views_admin.occurrence_status, name="occurrence-status"),
    path("occurrences/<int:occurrence_id>/delete/", views_admin.occurrence_delete, name="occurrence-delete"),
    path("slots/<int:slot_id>/edit/", views_admin.slot_update_view, name="slot-edit"),
    path("slots/<int:slot_id>/delete/", views_admin.slot_delete_view, name="slot-delete"),
    path("slots/<int:slot_id>/status/", views_admin.slot_status, name="slot-status"),
    path("slots/<int:slot_id>/responsable/assign/", views_admin.slot_assign_responsable, name="slot-assign-responsable"),
    path("slots/<int:slot_id>/responsable/release/", views_admin.slot_release_responsable, name="slot-release-responsable"),
]

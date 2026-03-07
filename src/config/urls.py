from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/django/", admin.site.urls),
    path("", include("accounts.urls")),
    path("sessions/", include("sessions.urls")),
    path("bookings/", include("bookings.urls")),
    path("admin/sessions/", include("sessions.urls_admin")),
    path("admin/bookings/", include("bookings.urls_admin")),
    path("admin/accounts/", include("accounts.urls_admin")),
    path("admin/audit/", include("audit.urls")),
]

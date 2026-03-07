from django.contrib import admin

from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("occurrence", "user", "status", "created_by_role", "created_at")
    list_filter = ("status", "created_by_role")
    search_fields = ("user__email", "user__full_name", "occurrence__label")

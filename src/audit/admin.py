from django.contrib import admin

from .models import AuditEntry


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ("action_type", "target_type", "target_id", "actor_user", "created_at")
    list_filter = ("action_type", "target_type", "actor_role_snapshot")
    search_fields = ("reason", "actor_user__email", "actor_user__full_name")

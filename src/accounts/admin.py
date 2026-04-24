from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("full_name", "email")
    list_display = ("full_name", "email", "role", "can_teach_courses", "is_active")
    search_fields = ("full_name", "email", "login_key")
    list_filter = ("role", "can_teach_courses", "is_active")
    readonly_fields = ("login_key",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Profile",
            {
                "fields": (
                    "full_name",
                    "login_key",
                    "role",
                    "can_teach_courses",
                    "password_state",
                )
            },
        ),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "role", "can_teach_courses", "password1", "password2"),
            },
        ),
    )

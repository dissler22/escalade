from django.conf import settings
from django.db import models


class AuditEntry(models.Model):
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_entries",
    )
    actor_role_snapshot = models.CharField(max_length=20)
    action_type = models.CharField(max_length=50)
    target_type = models.CharField(max_length=50)
    target_id = models.PositiveBigIntegerField()
    occurrence = models.ForeignKey(
        "club_sessions.SessionOccurrence",
        on_delete=models.CASCADE,
        related_name="audit_entries",
        null=True,
        blank=True,
    )
    reservation = models.ForeignKey(
        "bookings.Reservation",
        on_delete=models.CASCADE,
        related_name="audit_entries",
        null=True,
        blank=True,
    )
    reason = models.CharField(max_length=255, blank=True)
    metadata_snapshot = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.action_type} on {self.target_type}#{self.target_id}"

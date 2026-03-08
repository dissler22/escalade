from django.conf import settings
from django.db import models
from django.db.models import Q


class ActiveReservationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Reservation.Status.ACTIVE)


class Reservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"

    occurrence = models.ForeignKey(
        "club_sessions.SessionOccurrence",
        on_delete=models.CASCADE,
        related_name="reservations",
        null=True,
        blank=True,
    )
    slot = models.ForeignKey(
        "club_sessions.SessionSlot",
        on_delete=models.CASCADE,
        related_name="reservations",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_by_role = models.CharField(max_length=20)
    cancellation_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveReservationQuerySet.as_manager()

    class Meta:
        ordering = ["created_at", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["slot", "user"],
                condition=Q(status="active"),
                name="unique_active_reservation_per_user_slot",
            ),
            models.UniqueConstraint(
                fields=["occurrence", "user"],
                condition=Q(status="active"),
                name="unique_active_reservation_per_user_occurrence_v2",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} / {self.occurrence or self.slot or 'unassigned-reservation'}"

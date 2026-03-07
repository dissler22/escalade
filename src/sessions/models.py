import datetime as dt

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class SessionSeries(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    label = models.CharField(max_length=255)
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    default_capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_session_series",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.default_capacity < 1:
            raise ValidationError("Capacity must be positive.")
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def __str__(self) -> str:
        return self.label


class SessionOccurrence(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    series = models.ForeignKey(
        SessionSeries,
        on_delete=models.SET_NULL,
        related_name="occurrences",
        null=True,
        blank=True,
    )
    label = models.CharField(max_length=255)
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    is_override = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_session_occurrences",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["session_date", "start_time", "id"]
        unique_together = ("series", "session_date")

    def clean(self):
        if self.capacity < 1:
            raise ValidationError("Capacity must be positive.")
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    @property
    def starts_at(self):
        from django.utils import timezone

        return timezone.make_aware(
            dt.datetime.combine(self.session_date, self.start_time),
            timezone.get_current_timezone(),
        )

    @property
    def remaining_capacity(self) -> int:
        return max(0, self.capacity - self.reservations.active().count())

    @property
    def is_bookable(self) -> bool:
        from django.utils import timezone

        return (
            self.status == self.Status.OPEN
            and self.starts_at > timezone.now()
            and self.remaining_capacity > 0
        )

    def __str__(self) -> str:
        return f"{self.label} - {self.session_date}"

import datetime as dt

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

MAX_SLOT_DURATION = dt.timedelta(minutes=90)


class SessionSeries(models.Model):
    class SessionType(models.TextChoices):
        FREE_PRACTICE = "free_practice", "Pratique libre"
        COURSE = "course", "Cours"

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
    session_type = models.CharField(
        max_length=20,
        choices=SessionType.choices,
        default=SessionType.FREE_PRACTICE,
    )
    default_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_course_series",
    )
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
        if self.session_type == self.SessionType.FREE_PRACTICE and self.default_teacher_id is not None:
            raise ValidationError("Free practice series cannot have a default teacher.")

    @property
    def is_course(self) -> bool:
        return self.session_type == self.SessionType.COURSE

    @property
    def is_free_practice(self) -> bool:
        return self.session_type == self.SessionType.FREE_PRACTICE

    def __str__(self) -> str:
        return self.label


class CourseEnrollmentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=CourseEnrollment.Status.ACTIVE)


class CourseEnrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REMOVED = "removed", "Removed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    series = models.ForeignKey(
        SessionSeries,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_course_enrollments",
    )
    removed_at = models.DateTimeField(null=True, blank=True)
    removed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="removed_course_enrollments",
    )

    objects = CourseEnrollmentQuerySet.as_manager()

    class Meta:
        ordering = ["user__full_name", "series__label", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "series"],
                condition=Q(status="active"),
                name="unique_active_course_enrollment_per_user_series",
            )
        ]

    def clean(self):
        if self.series.session_type != SessionSeries.SessionType.COURSE:
            raise ValidationError("Course enrollments can only target course series.")

    def __str__(self) -> str:
        return f"{self.user} / {self.series}"


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
    session_type = models.CharField(
        max_length=20,
        choices=SessionSeries.SessionType.choices,
        default=SessionSeries.SessionType.FREE_PRACTICE,
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_occurrences",
    )
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
        if self.series is not None and self.session_type != self.series.session_type:
            raise ValidationError("Occurrence type must match its series type.")
        if self.session_type == SessionSeries.SessionType.FREE_PRACTICE and self.teacher_id is not None:
            raise ValidationError("Free practice occurrences cannot expose a teacher.")

    @property
    def starts_at(self):
        from django.utils import timezone

        return timezone.make_aware(
            dt.datetime.combine(self.session_date, self.start_time),
            timezone.get_current_timezone(),
        )

    @property
    def ends_at(self):
        from django.utils import timezone

        return timezone.make_aware(
            dt.datetime.combine(self.session_date, self.end_time),
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

    @property
    def coverage_summary(self) -> dict[str, int]:
        if self.session_type == SessionSeries.SessionType.COURSE:
            return {"covered": 0, "uncovered": 0, "cancelled": 0, "total": 0}
        covered = 0
        uncovered = 0
        cancelled = 0
        for slot in self.slots.all():
            if slot.coverage_status == SessionSlot.CoverageStatus.CANCELLED:
                cancelled += 1
            elif slot.coverage_status == SessionSlot.CoverageStatus.COVERED:
                covered += 1
            else:
                uncovered += 1
        return {
            "covered": covered,
            "uncovered": uncovered,
            "cancelled": cancelled,
            "total": covered + uncovered + cancelled,
        }

    def __str__(self) -> str:
        return f"{self.label} - {self.session_date}"

    @property
    def is_course(self) -> bool:
        return self.session_type == SessionSeries.SessionType.COURSE

    @property
    def is_free_practice(self) -> bool:
        return self.session_type == SessionSeries.SessionType.FREE_PRACTICE

    @property
    def display_teacher(self):
        if self.teacher is not None:
            return self.teacher
        if self.series is not None:
            return self.series.default_teacher
        return None


class SessionSlot(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    class CoverageStatus(models.TextChoices):
        UNCOVERED = "uncovered", "Uncovered"
        COVERED = "covered", "Covered"
        CANCELLED = "cancelled", "Cancelled"

    occurrence = models.ForeignKey(
        SessionOccurrence,
        on_delete=models.CASCADE,
        related_name="slots",
    )
    sequence_index = models.PositiveIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    auto_cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["occurrence__session_date", "start_time", "sequence_index", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["occurrence", "sequence_index"],
                name="unique_slot_sequence_per_occurrence",
            )
        ]

    def clean(self):
        if self.capacity < 1:
            raise ValidationError("Capacity must be positive.")
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        if self.occurrence and self.occurrence.session_type != SessionSeries.SessionType.FREE_PRACTICE:
            raise ValidationError("Slots are reserved for free practice occurrences.")
        start_dt = dt.datetime.combine(self.occurrence.session_date, self.start_time)
        end_dt = dt.datetime.combine(self.occurrence.session_date, self.end_time)
        if end_dt - start_dt > MAX_SLOT_DURATION:
            raise ValidationError("A slot cannot exceed 90 minutes.")

    @property
    def starts_at(self):
        from django.utils import timezone

        return timezone.make_aware(
            dt.datetime.combine(self.occurrence.session_date, self.start_time),
            timezone.get_current_timezone(),
        )

    @property
    def ends_at(self):
        from django.utils import timezone

        return timezone.make_aware(
            dt.datetime.combine(self.occurrence.session_date, self.end_time),
            timezone.get_current_timezone(),
        )

    @property
    def remaining_capacity(self) -> int:
        return self.occurrence.remaining_capacity

    @property
    def current_responsable_assignment(self):
        return self.responsable_assignments.filter(status=ResponsibleAssignment.Status.ACTIVE).first()

    @property
    def current_responsable(self):
        assignment = self.current_responsable_assignment
        return assignment.user if assignment else None

    @property
    def coverage_status(self) -> str:
        if self.status == self.Status.CANCELLED:
            return self.CoverageStatus.CANCELLED
        if self.current_responsable_assignment is not None:
            return self.CoverageStatus.COVERED
        return self.CoverageStatus.UNCOVERED

    @property
    def is_bookable(self) -> bool:
        from django.utils import timezone

        return (
            self.status == self.Status.OPEN
            and self.starts_at > timezone.now()
            and self.remaining_capacity > 0
        )

    def __str__(self) -> str:
        return f"{self.occurrence.label} #{self.sequence_index}"


class ResponsibleAssignment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RELEASED = "released", "Released"
        REVOKED = "revoked", "Revoked"

    slot = models.ForeignKey(
        SessionSlot,
        on_delete=models.CASCADE,
        related_name="responsable_assignments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="responsable_assignments",
    )
    assigned_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responsable_assignment_actions",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    release_reason = models.CharField(max_length=255, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-assigned_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["slot"],
                condition=Q(status="active"),
                name="unique_active_responsable_per_slot",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} / {self.slot}"


class EmailAutomationSettings(models.Model):
    reminder_days_before = models.PositiveSmallIntegerField(default=7)
    cancellation_days_before = models.PositiveSmallIntegerField(default=2)
    reminder_email_subject = models.CharField(
        max_length=255,
        default="Creneau sans responsable le {session_date}",
    )
    reminder_email_body = models.TextField(
        default=(
            "Bonjour,\n\n"
            "Le creneau {slot_start}-{slot_end} de {session_label} le {session_date} "
            "n a pas encore de responsable.\n"
            "Merci de vous positionner si vous pouvez le couvrir."
        )
    )
    cancellation_email_subject = models.CharField(
        max_length=255,
        default="Annulation du creneau {session_label}",
    )
    cancellation_email_body = models.TextField(
        default=(
            "Bonjour,\n\n"
            "Le creneau {slot_start}-{slot_end} de {session_label} le {session_date} "
            "est annule faute de responsable.\n"
            "Merci de votre comprehension."
        )
    )
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.reminder_days_before <= self.cancellation_days_before:
            raise ValidationError("Le rappel doit partir avant l annulation automatique.")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return "Email automation settings"

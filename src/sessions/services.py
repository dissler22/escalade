import datetime as dt

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from audit.services import record_event

from .models import SessionOccurrence, SessionSeries


def list_member_open_occurrences():
    today = timezone.localdate()
    current_time = timezone.localtime().time()
    return (
        SessionOccurrence.objects.annotate(
            active_reservations=Count("reservations", filter=Q(reservations__status="active"))
        )
        .filter(
            status=SessionOccurrence.Status.OPEN,
        )
        .filter(
            Q(session_date__gt=today)
            | Q(session_date=today, start_time__gt=current_time)
        )
        .order_by("session_date", "start_time")
    )


def list_member_reservations(user):
    return user.reservations.filter(status="active").select_related("occurrence").order_by(
        "occurrence__session_date", "occurrence__start_time"
    )


def get_member_occurrence_or_404(queryset, pk):
    return queryset.get(pk=pk)


def create_series(*, actor, cleaned_data, weeks=8):
    with transaction.atomic():
        series = SessionSeries.objects.create(created_by=actor, **cleaned_data)
        generate_future_occurrences(series=series, actor=actor, weeks=weeks)
        record_event(
            actor=actor,
            action_type="session_series_created",
            target_type="session_series",
            target_id=series.pk,
            metadata={"label": series.label, "default_capacity": series.default_capacity},
        )
        return series


def update_series(*, actor, series, cleaned_data):
    for field, value in cleaned_data.items():
        setattr(series, field, value)
    series.full_clean()
    series.save()
    record_event(
        actor=actor,
        action_type="session_series_updated",
        target_type="session_series",
        target_id=series.pk,
        metadata={"label": series.label, "default_capacity": series.default_capacity},
    )
    return series


def generate_future_occurrences(*, series, actor, weeks=8):
    base_date = timezone.localdate()
    created = []
    for offset in range(0, weeks):
        day = base_date + dt.timedelta(days=offset * 7)
        target_date = day + dt.timedelta((series.weekday - day.weekday()) % 7)
        occurrence, was_created = SessionOccurrence.objects.get_or_create(
            series=series,
            session_date=target_date,
            defaults={
                "label": series.label,
                "start_time": series.start_time,
                "end_time": series.end_time,
                "capacity": series.default_capacity,
                "status": SessionOccurrence.Status.DRAFT,
                "created_by": actor,
            },
        )
        if was_created:
            created.append(occurrence)
    return created


def create_occurrence(*, actor, cleaned_data):
    occurrence = SessionOccurrence.objects.create(created_by=actor, **cleaned_data)
    record_event(
        actor=actor,
        action_type="session_occurrence_created",
        target_type="session_occurrence",
        target_id=occurrence.pk,
        occurrence=occurrence,
        metadata={"label": occurrence.label, "capacity": occurrence.capacity, "status": occurrence.status},
    )
    return occurrence


def update_occurrence(*, actor, occurrence, cleaned_data, mark_override=False):
    active_count = occurrence.reservations.active().count()
    new_capacity = cleaned_data.get("capacity", occurrence.capacity)
    if new_capacity < active_count:
        raise ValidationError("La capacite ne peut pas etre inferieure aux reservations actives.")
    for field, value in cleaned_data.items():
        setattr(occurrence, field, value)
    if mark_override:
        occurrence.is_override = True
    occurrence.full_clean()
    occurrence.save()
    record_event(
        actor=actor,
        action_type="session_occurrence_updated",
        target_type="session_occurrence",
        target_id=occurrence.pk,
        occurrence=occurrence,
        metadata={"capacity": occurrence.capacity, "status": occurrence.status, "is_override": occurrence.is_override},
    )
    return occurrence


def change_occurrence_status(*, actor, occurrence, status, reason=""):
    if status not in SessionOccurrence.Status.values:
        raise ValidationError("Statut invalide.")
    occurrence.status = status
    occurrence.save(update_fields=["status", "updated_at"])
    record_event(
        actor=actor,
        action_type=f"session_occurrence_{status}",
        target_type="session_occurrence",
        target_id=occurrence.pk,
        occurrence=occurrence,
        reason=reason,
        metadata={"status": status},
    )
    return occurrence

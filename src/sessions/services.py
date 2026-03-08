import datetime as dt
from dataclasses import dataclass
from urllib.parse import urlencode

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Prefetch, Q
from django.urls import reverse
from django.utils import formats, timezone

from audit.services import record_event
from bookings.models import Reservation

from .models import (
    MAX_SLOT_DURATION,
    EmailAutomationSettings,
    ResponsibleAssignment,
    SessionOccurrence,
    SessionSeries,
    SessionSlot,
)

VISIBLE_DAY_START = dt.time(hour=8, minute=0)
VISIBLE_DAY_END = dt.time(hour=23, minute=0)
VISIBLE_RANGE_MINUTES = (
    VISIBLE_DAY_END.hour * 60
    + VISIBLE_DAY_END.minute
    - VISIBLE_DAY_START.hour * 60
    - VISIBLE_DAY_START.minute
)


@dataclass(slots=True)
class CalendarOccurrenceBlock:
    occurrence: SessionOccurrence
    occurrence_id: int
    display_label_short: str
    status_label: str
    status_class: str
    start_time: dt.time
    end_time: dt.time
    time_label: str
    starts_before_visible_range: bool
    ends_after_visible_range: bool
    is_selected: bool
    is_bookable: bool
    remaining_capacity: int
    covered_slots: int
    total_slots: int


@dataclass(slots=True)
class CalendarDay:
    date: dt.date
    label_short: str
    label_full: str
    is_today: bool
    occurrence_blocks: list[CalendarOccurrenceBlock]


@dataclass(slots=True)
class CalendarWeek:
    week_start: dt.date
    week_end: dt.date
    week_start_iso: str
    week_end_iso: str
    visible_start_time: dt.time
    visible_end_time: dt.time
    visible_start_label: str
    visible_end_label: str
    previous_week_start: dt.date
    previous_week_start_iso: str
    next_week_start: dt.date
    next_week_start_iso: str
    selected_occurrence_id: int | None
    days: list[CalendarDay]
    hour_markers: list[dict[str, float | str]]


@dataclass(slots=True)
class InlineSlotCard:
    slot: SessionSlot
    slot_id: int
    time_label: str
    coverage_status: str
    coverage_label: str
    coverage_class: str
    current_responsable_name: str
    my_assignment: ResponsibleAssignment | None
    action_state: str
    can_take: bool
    can_release: bool


@dataclass(slots=True)
class InlineOccurrenceDetail:
    occurrence: SessionOccurrence
    occurrence_id: int
    title: str
    date_label: str
    time_label: str
    status_label: str
    status_class: str
    remaining_capacity_label: str
    coverage_summary_label: str
    notes: str
    my_reservation: Reservation | None
    slot_cards: list[InlineSlotCard]
    can_reserve: bool
    can_cancel: bool
    week_start_iso: str


@dataclass(slots=True)
class CalendarPageState:
    week: CalendarWeek
    selected_detail: InlineOccurrenceDetail | None
    empty_state_message: str
    has_occurrences: bool


def _time_to_minutes(value: dt.time) -> int:
    return value.hour * 60 + value.minute


def _week_start_for(value: dt.date) -> dt.date:
    return value - dt.timedelta(days=value.weekday())


def normalize_week_start(value, *, reference_date: dt.date | None = None) -> dt.date:
    if reference_date is None:
        reference_date = timezone.localdate()
    if isinstance(value, dt.date):
        return _week_start_for(value)
    if value:
        try:
            return _week_start_for(dt.date.fromisoformat(str(value)))
        except (TypeError, ValueError):
            pass
    return _week_start_for(reference_date)


def normalize_selected_occurrence(value) -> int | None:
    if value in (None, ""):
        return None
    try:
        selected = int(value)
    except (TypeError, ValueError):
        return None
    return selected if selected > 0 else None


def get_occurrence_week_start(occurrence: SessionOccurrence) -> dt.date:
    return _week_start_for(occurrence.session_date)


def resolve_calendar_return_context(
    *,
    week_start_value=None,
    selected_occurrence_value=None,
    occurrence: SessionOccurrence | None = None,
) -> dict[str, dt.date | int | str | None]:
    reference_date = occurrence.session_date if occurrence is not None else timezone.localdate()
    week_start = normalize_week_start(week_start_value, reference_date=reference_date)
    selected_occurrence = normalize_selected_occurrence(selected_occurrence_value)
    if selected_occurrence is None and occurrence is not None:
        selected_occurrence = occurrence.pk
    return {
        "week_start": week_start,
        "week_start_iso": week_start.isoformat(),
        "selected_occurrence": selected_occurrence,
    }


def build_member_calendar_url(
    *,
    week_start: dt.date | None = None,
    selected_occurrence: int | None = None,
    occurrence: SessionOccurrence | None = None,
    anchor: str | None = None,
) -> str:
    if week_start is None:
        if occurrence is not None:
            week_start = get_occurrence_week_start(occurrence)
        else:
            week_start = normalize_week_start(None)
    params: dict[str, str | int] = {"week_start": week_start.isoformat()}
    if selected_occurrence is None and occurrence is not None:
        selected_occurrence = occurrence.pk
    if selected_occurrence is not None:
        params["selected_occurrence"] = selected_occurrence
    url = f"{reverse('sessions:session-list')}?{urlencode(params)}"
    if anchor:
        return f"{url}#{anchor}"
    return url


def _member_calendar_statuses() -> tuple[str, ...]:
    return (
        SessionOccurrence.Status.OPEN,
        SessionOccurrence.Status.CLOSED,
        SessionOccurrence.Status.CANCELLED,
    )


def _member_occurrence_queryset(*, start_date=None, end_date=None, today=None, current_time=None):
    if today is None:
        today = timezone.localdate()
    if current_time is None:
        current_time = timezone.localtime().time()
    active_reservations = Reservation.objects.active().select_related("user")
    active_assignments = ResponsibleAssignment.objects.filter(
        status=ResponsibleAssignment.Status.ACTIVE
    ).select_related("user")
    queryset = (
        SessionOccurrence.objects.prefetch_related(
            Prefetch("reservations", queryset=active_reservations),
            Prefetch("slots__reservations", queryset=active_reservations),
            Prefetch("slots__responsable_assignments", queryset=active_assignments),
        )
        .filter(status__in=_member_calendar_statuses())
        .filter(_future_occurrence_filter(today=today, current_time=current_time))
        .order_by("session_date", "start_time", "id")
    )
    if start_date is not None:
        queryset = queryset.filter(session_date__gte=start_date)
    if end_date is not None:
        queryset = queryset.filter(session_date__lte=end_date)
    return queryset


def _occurrence_active_reservations(occurrence: SessionOccurrence) -> list[Reservation]:
    return list(occurrence.reservations.all())


def _occurrence_remaining_capacity(occurrence: SessionOccurrence) -> int:
    return max(0, occurrence.capacity - len(_occurrence_active_reservations(occurrence)))


def _occurrence_is_bookable(occurrence: SessionOccurrence) -> bool:
    return (
        occurrence.status == SessionOccurrence.Status.OPEN
        and occurrence.starts_at > timezone.now()
        and _occurrence_remaining_capacity(occurrence) > 0
    )


def _active_slot_assignment(slot: SessionSlot) -> ResponsibleAssignment | None:
    for assignment in slot.responsable_assignments.all():
        if assignment.status == ResponsibleAssignment.Status.ACTIVE:
            return assignment
    return None


def _slot_coverage_status(slot: SessionSlot) -> str:
    if slot.status == SessionSlot.Status.CANCELLED:
        return SessionSlot.CoverageStatus.CANCELLED
    if _active_slot_assignment(slot) is not None:
        return SessionSlot.CoverageStatus.COVERED
    return SessionSlot.CoverageStatus.UNCOVERED


def _coverage_summary(occurrence: SessionOccurrence) -> dict[str, int]:
    covered = 0
    uncovered = 0
    cancelled = 0
    for slot in occurrence.slots.all():
        coverage_status = _slot_coverage_status(slot)
        if coverage_status == SessionSlot.CoverageStatus.CANCELLED:
            cancelled += 1
        elif coverage_status == SessionSlot.CoverageStatus.COVERED:
            covered += 1
        else:
            uncovered += 1
    return {
        "covered": covered,
        "uncovered": uncovered,
        "cancelled": cancelled,
        "total": covered + uncovered + cancelled,
    }


def _occurrence_status_summary(occurrence: SessionOccurrence) -> tuple[str, str]:
    remaining_capacity = _occurrence_remaining_capacity(occurrence)
    if occurrence.status == SessionOccurrence.Status.CANCELLED:
        return ("Annulee", "status-danger")
    if occurrence.status == SessionOccurrence.Status.CLOSED:
        return ("Fermee", "status-warning")
    if remaining_capacity == 0:
        return ("Complet", "status-danger")
    return ("", "status-open")


def _shorten_occurrence_label(label: str) -> str:
    shortened = " ".join(label.split())
    for prefix in ("Pratique libre", "pratique libre", "Seance", "seance", "Session", "session"):
        if shortened.startswith(prefix):
            shortened = shortened[len(prefix) :].strip(" :-")
    if not shortened:
        shortened = "Seance"
    if len(shortened) > 22:
        return f"{shortened[:19].rstrip()}..."
    return shortened


def _build_day_blocks(day_occurrences: list[SessionOccurrence], *, selected_occurrence_id: int | None) -> list[CalendarOccurrenceBlock]:
    blocks: list[CalendarOccurrenceBlock] = []
    for occurrence in sorted(day_occurrences, key=lambda item: (item.start_time, item.end_time, item.id)):
        status_label, status_class = _occurrence_status_summary(occurrence)
        coverage_summary = _coverage_summary(occurrence)
        remaining_capacity = _occurrence_remaining_capacity(occurrence)
        blocks.append(
            CalendarOccurrenceBlock(
                occurrence=occurrence,
                occurrence_id=occurrence.id,
                display_label_short=_shorten_occurrence_label(occurrence.label),
                status_label=status_label,
                status_class=status_class,
                start_time=occurrence.start_time,
                end_time=occurrence.end_time,
                time_label=f"{occurrence.start_time:%H:%M} - {occurrence.end_time:%H:%M}",
                starts_before_visible_range=occurrence.start_time < VISIBLE_DAY_START,
                ends_after_visible_range=occurrence.end_time > VISIBLE_DAY_END,
                is_selected=occurrence.id == selected_occurrence_id,
                is_bookable=_occurrence_is_bookable(occurrence),
                remaining_capacity=remaining_capacity,
                covered_slots=coverage_summary["covered"],
                total_slots=coverage_summary["total"],
            )
        )
    return blocks


def _build_inline_detail(*, occurrence: SessionOccurrence, user, week_start: dt.date) -> InlineOccurrenceDetail:
    my_reservation = next(
        (reservation for reservation in occurrence.reservations.all() if reservation.user_id == user.id),
        None,
    )
    slot_cards: list[InlineSlotCard] = []
    for slot in occurrence.slots.all():
        active_assignment = _active_slot_assignment(slot)
        my_assignment = active_assignment if active_assignment and active_assignment.user_id == user.id else None
        coverage_status = _slot_coverage_status(slot)
        if coverage_status == SessionSlot.CoverageStatus.CANCELLED:
            coverage_label = "Creneau annule"
            coverage_class = "status-neutral"
        elif my_assignment is not None:
            coverage_label = "Vous couvrez ce creneau"
            coverage_class = "status-warning"
        elif active_assignment is not None:
            coverage_label = "Responsable confirme"
            coverage_class = "status-success"
        else:
            coverage_label = "Responsable manque"
            coverage_class = "status-danger"

        can_take = (
            user.can_cover_slots
            and coverage_status == SessionSlot.CoverageStatus.UNCOVERED
            and slot.starts_at > timezone.now()
        )
        can_release = my_assignment is not None and slot.starts_at > timezone.now()
        action_state = "release" if can_release else "take" if can_take else "none"
        slot_cards.append(
            InlineSlotCard(
                slot=slot,
                slot_id=slot.id,
                time_label=f"{slot.start_time:%H:%M} - {slot.end_time:%H:%M}",
                coverage_status=coverage_status,
                coverage_label=coverage_label,
                coverage_class=coverage_class,
                current_responsable_name=active_assignment.user.full_name if active_assignment else "",
                my_assignment=my_assignment,
                action_state=action_state,
                can_take=can_take,
                can_release=can_release,
            )
        )

    status_label, status_class = _occurrence_status_summary(occurrence)
    coverage_summary = _coverage_summary(occurrence)
    remaining_capacity = _occurrence_remaining_capacity(occurrence)
    return InlineOccurrenceDetail(
        occurrence=occurrence,
        occurrence_id=occurrence.id,
        title=occurrence.label,
        date_label=formats.date_format(occurrence.session_date, "l j F"),
        time_label=f"{occurrence.start_time:%H:%M} - {occurrence.end_time:%H:%M}",
        status_label=status_label,
        status_class=status_class,
        remaining_capacity_label=f"{remaining_capacity} place(s) restante(s)",
        coverage_summary_label=(
            f"{coverage_summary['covered']}/{coverage_summary['total']} creneau(x) avec responsable"
        ),
        notes=occurrence.notes.strip(),
        my_reservation=my_reservation,
        slot_cards=slot_cards,
        can_reserve=my_reservation is None and _occurrence_is_bookable(occurrence),
        can_cancel=my_reservation is not None,
        week_start_iso=week_start.isoformat(),
    )


def build_member_calendar_page(*, user, week_start_value=None, selected_occurrence_value=None) -> CalendarPageState:
    week_start = normalize_week_start(week_start_value)
    week_end = week_start + dt.timedelta(days=6)
    occurrences = list(_member_occurrence_queryset(start_date=week_start, end_date=week_end))
    requested_occurrence_id = normalize_selected_occurrence(selected_occurrence_value)

    selected_occurrence = next(
        (occurrence for occurrence in occurrences if occurrence.id == requested_occurrence_id),
        None,
    )
    if selected_occurrence is None and occurrences:
        selected_occurrence = occurrences[0]
    selected_occurrence_id = selected_occurrence.id if selected_occurrence is not None else None

    days: list[CalendarDay] = []
    today = timezone.localdate()
    for offset in range(7):
        current_date = week_start + dt.timedelta(days=offset)
        day_occurrences = [occurrence for occurrence in occurrences if occurrence.session_date == current_date]
        days.append(
            CalendarDay(
                date=current_date,
                label_short=formats.date_format(current_date, "D j"),
                label_full=formats.date_format(current_date, "l j F"),
                is_today=current_date == today,
                occurrence_blocks=_build_day_blocks(
                    day_occurrences,
                    selected_occurrence_id=selected_occurrence_id,
                ),
            )
        )

    week = CalendarWeek(
        week_start=week_start,
        week_end=week_end,
        week_start_iso=week_start.isoformat(),
        week_end_iso=week_end.isoformat(),
        visible_start_time=VISIBLE_DAY_START,
        visible_end_time=VISIBLE_DAY_END,
        visible_start_label=f"{VISIBLE_DAY_START:%H:%M}",
        visible_end_label=f"{VISIBLE_DAY_END:%H:%M}",
        previous_week_start=week_start - dt.timedelta(days=7),
        previous_week_start_iso=(week_start - dt.timedelta(days=7)).isoformat(),
        next_week_start=week_start + dt.timedelta(days=7),
        next_week_start_iso=(week_start + dt.timedelta(days=7)).isoformat(),
        selected_occurrence_id=selected_occurrence_id,
        days=days,
        hour_markers=[],
    )
    selected_detail = (
        _build_inline_detail(occurrence=selected_occurrence, user=user, week_start=week_start)
        if selected_occurrence is not None
        else None
    )
    return CalendarPageState(
        week=week,
        selected_detail=selected_detail,
        empty_state_message="Aucune seance visible sur cette semaine.",
        has_occurrences=bool(occurrences),
    )


def _future_occurrence_filter(*, today=None, current_time=None) -> Q:
    if today is None:
        today = timezone.localdate()
    if current_time is None:
        current_time = timezone.localtime().time()
    return Q(session_date__gt=today) | Q(session_date=today, end_time__gt=current_time)


def _future_slot_filter(*, today=None, current_time=None, prefix=""):
    if today is None:
        today = timezone.localdate()
    if current_time is None:
        current_time = timezone.localtime().time()
    return Q(**{f"{prefix}occurrence__session_date__gt": today}) | Q(
        **{
            f"{prefix}occurrence__session_date": today,
            f"{prefix}end_time__gt": current_time,
        }
    )


def _get_slot_segments(*, session_date, start_time, end_time):
    start_dt = dt.datetime.combine(session_date, start_time)
    end_dt = dt.datetime.combine(session_date, end_time)
    if end_dt <= start_dt:
        raise ValidationError("End time must be after start time.")
    segments = []
    current = start_dt
    sequence = 1
    while current < end_dt:
        next_end = min(current + MAX_SLOT_DURATION, end_dt)
        segments.append(
            {
                "sequence_index": sequence,
                "start_time": current.time(),
                "end_time": next_end.time(),
            }
        )
        current = next_end
        sequence += 1
    return segments


def _slot_has_commitments(slot):
    return slot.reservations.active().exists() or slot.responsable_assignments.filter(
        status=ResponsibleAssignment.Status.ACTIVE
    ).exists()


def _assert_slot_inside_occurrence(occurrence, start_time, end_time):
    if start_time < occurrence.start_time or end_time > occurrence.end_time:
        raise ValidationError("Le creneau doit rester inclus dans la seance.")


def _assert_slot_does_not_overlap(slot, *, occurrence, start_time, end_time):
    overlaps = occurrence.slots.exclude(pk=slot.pk).filter(
        start_time__lt=end_time,
        end_time__gt=start_time,
    )
    if overlaps.exists():
        raise ValidationError("Le creneau chevauche un autre creneau existant.")


def list_member_open_occurrences():
    today = timezone.localdate()
    current_time = timezone.localtime().time()
    active_reservations = Reservation.objects.active().select_related("user")
    active_assignments = ResponsibleAssignment.objects.filter(
        status=ResponsibleAssignment.Status.ACTIVE
    ).select_related("user")
    return (
        SessionOccurrence.objects.prefetch_related(
            Prefetch("slots__reservations", queryset=active_reservations),
            Prefetch("slots__responsable_assignments", queryset=active_assignments),
        )
        .filter(status=SessionOccurrence.Status.OPEN)
        .filter(_future_occurrence_filter(today=today, current_time=current_time))
        .order_by("session_date", "start_time")
    )


def list_member_reservations(user):
    return (
        user.reservations.filter(status=Reservation.Status.ACTIVE)
        .select_related("occurrence")
        .order_by("occurrence__session_date", "occurrence__start_time")
    )


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
                "status": SessionOccurrence.Status.OPEN,
                "created_by": actor,
            },
        )
        if was_created:
            sync_occurrence_slots(actor=actor, occurrence=occurrence)
            created.append(occurrence)
    return created


def sync_occurrence_slots(*, actor, occurrence):
    expected_segments = _get_slot_segments(
        session_date=occurrence.session_date,
        start_time=occurrence.start_time,
        end_time=occurrence.end_time,
    )
    existing_slots = list(occurrence.slots.order_by("sequence_index"))
    existing_signature = [(slot.sequence_index, slot.start_time, slot.end_time) for slot in existing_slots]
    expected_signature = [
        (segment["sequence_index"], segment["start_time"], segment["end_time"])
        for segment in expected_segments
    ]

    if existing_slots and existing_signature != expected_signature:
        if any(_slot_has_commitments(slot) for slot in existing_slots):
            raise ValidationError(
                "Impossible de recalculer automatiquement les creneaux avec des reservations ou responsabilites actives."
            )
        occurrence.slots.all().delete()
        existing_slots = []

    if not existing_slots:
        created_slots = []
        for segment in expected_segments:
            slot = SessionSlot.objects.create(
                occurrence=occurrence,
                sequence_index=segment["sequence_index"],
                start_time=segment["start_time"],
                end_time=segment["end_time"],
                capacity=occurrence.capacity,
                status=occurrence.status,
            )
            created_slots.append(slot)
            record_event(
                actor=actor,
                action_type="slot_created",
                target_type="session_slot",
                target_id=slot.pk,
                occurrence=occurrence,
                slot=slot,
                metadata={"sequence_index": slot.sequence_index, "status": slot.status},
            )
        return created_slots

    updated_slots = []
    for slot, segment in zip(existing_slots, expected_segments, strict=True):
        active_count = slot.reservations.active().count()
        if occurrence.capacity < active_count:
            raise ValidationError("La capacite ne peut pas etre inferieure aux reservations actives d un creneau.")
        changed = False
        for field in ("sequence_index", "start_time", "end_time"):
            new_value = segment[field]
            if getattr(slot, field) != new_value:
                setattr(slot, field, new_value)
                changed = True
        if slot.capacity != occurrence.capacity:
            slot.capacity = occurrence.capacity
            changed = True
        if slot.status != occurrence.status and slot.status not in {
            SessionSlot.Status.CANCELLED,
            SessionSlot.Status.COMPLETED,
        }:
            slot.status = occurrence.status
            changed = True
        if changed:
            slot.full_clean()
            slot.save()
            record_event(
                actor=actor,
                action_type="slot_updated",
                target_type="session_slot",
                target_id=slot.pk,
                occurrence=occurrence,
                slot=slot,
                metadata={"sequence_index": slot.sequence_index, "status": slot.status},
            )
        updated_slots.append(slot)
    return updated_slots


def create_occurrence(*, actor, cleaned_data):
    with transaction.atomic():
        occurrence = SessionOccurrence.objects.create(created_by=actor, **cleaned_data)
        sync_occurrence_slots(actor=actor, occurrence=occurrence)
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
    active_count = sum(slot.reservations.active().count() for slot in occurrence.slots.all())
    new_capacity = cleaned_data.get("capacity", occurrence.capacity)
    if new_capacity < 1:
        raise ValidationError("La capacite doit etre strictement positive.")
    if active_count and new_capacity < max(slot.reservations.active().count() for slot in occurrence.slots.all()):
        raise ValidationError("La capacite ne peut pas etre inferieure aux reservations actives d un creneau.")
    for field, value in cleaned_data.items():
        setattr(occurrence, field, value)
    if mark_override:
        occurrence.is_override = True
    occurrence.full_clean()
    with transaction.atomic():
        occurrence.save()
        sync_occurrence_slots(actor=actor, occurrence=occurrence)
        record_event(
            actor=actor,
            action_type="session_occurrence_updated",
            target_type="session_occurrence",
            target_id=occurrence.pk,
            occurrence=occurrence,
            metadata={
                "capacity": occurrence.capacity,
                "status": occurrence.status,
                "is_override": occurrence.is_override,
            },
        )
    return occurrence


def change_occurrence_status(*, actor, occurrence, status, reason=""):
    if status not in SessionOccurrence.Status.values:
        raise ValidationError("Statut invalide.")
    with transaction.atomic():
        occurrence.status = status
        occurrence.save(update_fields=["status", "updated_at"])
        for slot in occurrence.slots.exclude(status=SessionSlot.Status.COMPLETED):
            if slot.status == SessionSlot.Status.CANCELLED and status != SessionOccurrence.Status.CANCELLED:
                continue
            slot.status = status
            if status == SessionOccurrence.Status.CANCELLED and slot.auto_cancelled_at is None:
                slot.auto_cancelled_at = timezone.now()
            slot.save(update_fields=["status", "auto_cancelled_at", "updated_at"])
            record_event(
                actor=actor,
                action_type=f"slot_{status}",
                target_type="session_slot",
                target_id=slot.pk,
                occurrence=occurrence,
                slot=slot,
                reason=reason,
                metadata={"status": status},
            )
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


def update_slot(*, actor, slot, cleaned_data):
    active_count = slot.reservations.active().count()
    new_capacity = cleaned_data.get("capacity", slot.capacity)
    if new_capacity < active_count:
        raise ValidationError("La capacite ne peut pas etre inferieure aux reservations actives.")

    new_start_time = cleaned_data.get("start_time", slot.start_time)
    new_end_time = cleaned_data.get("end_time", slot.end_time)
    if new_end_time <= new_start_time:
        raise ValidationError("La fin doit etre apres le debut.")
    if dt.datetime.combine(slot.occurrence.session_date, new_end_time) - dt.datetime.combine(
        slot.occurrence.session_date, new_start_time
    ) > MAX_SLOT_DURATION:
        raise ValidationError("Un creneau ne peut pas depasser 90 minutes.")
    _assert_slot_inside_occurrence(slot.occurrence, new_start_time, new_end_time)
    _assert_slot_does_not_overlap(slot, occurrence=slot.occurrence, start_time=new_start_time, end_time=new_end_time)

    with transaction.atomic():
        for field, value in cleaned_data.items():
            setattr(slot, field, value)
        slot.full_clean()
        slot.save()
        record_event(
            actor=actor,
            action_type="slot_updated",
            target_type="session_slot",
            target_id=slot.pk,
            occurrence=slot.occurrence,
            slot=slot,
            metadata={"status": slot.status, "capacity": slot.capacity},
        )
    return slot


def change_slot_status(*, actor, slot, status, reason="", automatic=False):
    if status not in SessionSlot.Status.values:
        raise ValidationError("Statut invalide.")
    slot.status = status
    if status == SessionSlot.Status.CANCELLED:
        slot.auto_cancelled_at = slot.auto_cancelled_at or timezone.now()
    update_fields = ["status", "updated_at"]
    if status == SessionSlot.Status.CANCELLED:
        update_fields.append("auto_cancelled_at")
    slot.save(update_fields=update_fields)
    record_event(
        actor=actor,
        action_type="slot_auto_cancelled_uncovered" if automatic and status == SessionSlot.Status.CANCELLED else f"slot_{status}",
        target_type="session_slot",
        target_id=slot.pk,
        occurrence=slot.occurrence,
        slot=slot,
        reason=reason,
        metadata={"status": status},
    )
    return slot


def _validate_responsable_assignment(*, user, slot):
    if slot.status == SessionSlot.Status.CANCELLED:
        raise ValidationError("Le creneau est annule.")
    if slot.status == SessionSlot.Status.COMPLETED:
        raise ValidationError("Le creneau est termine.")
    if slot.starts_at <= timezone.now():
        raise ValidationError("Le creneau a deja commence.")
    if not user.can_cover_slots:
        raise ValidationError("Vous n etes pas accredite responsable.")
    if slot.responsable_assignments.filter(status=ResponsibleAssignment.Status.ACTIVE).exists():
        raise ValidationError("Ce creneau a deja un responsable.")


def take_slot_responsibility(*, user, slot):
    with transaction.atomic():
        locked_slot = SessionSlot.objects.select_for_update().get(pk=slot.pk)
        _validate_responsable_assignment(user=user, slot=locked_slot)
        assignment = ResponsibleAssignment.objects.create(
            slot=locked_slot,
            user=user,
            assigned_by_user=user,
        )
        record_event(
            actor=user,
            action_type="responsable_assignment_taken",
            target_type="responsible_assignment",
            target_id=assignment.pk,
            occurrence=locked_slot.occurrence,
            slot=locked_slot,
            responsible_assignment=assignment,
            metadata={"slot_id": locked_slot.pk, "user_id": user.pk},
        )
        return assignment


def release_slot_responsibility(*, actor, slot, user=None, reason="responsable_released"):
    target_user = user or actor
    with transaction.atomic():
        assignment = (
            ResponsibleAssignment.objects.select_for_update()
            .filter(slot=slot, user=target_user, status=ResponsibleAssignment.Status.ACTIVE)
            .first()
        )
        if assignment is None:
            raise ResponsibleAssignment.DoesNotExist()
        if slot.starts_at <= timezone.now():
            raise ValidationError("Le creneau a deja commence.")
        assignment.status = (
            ResponsibleAssignment.Status.REVOKED
            if actor != target_user or reason == "responsable_accreditation_revoked"
            else ResponsibleAssignment.Status.RELEASED
        )
        assignment.release_reason = reason
        assignment.released_at = timezone.now()
        assignment.save(update_fields=["status", "release_reason", "released_at"])
        record_event(
            actor=actor,
            action_type="responsable_assignment_revoked"
            if assignment.status == ResponsibleAssignment.Status.REVOKED
            else "responsable_assignment_released",
            target_type="responsible_assignment",
            target_id=assignment.pk,
            occurrence=slot.occurrence,
            slot=slot,
            responsible_assignment=assignment,
            reason=reason,
            metadata={"slot_id": slot.pk, "user_id": target_user.pk},
        )
        return assignment


def assign_slot_responsibility(*, actor, slot, user):
    if not user.can_cover_slots:
        raise ValidationError("Le compte choisi ne peut pas devenir responsable.")
    with transaction.atomic():
        locked_slot = SessionSlot.objects.select_for_update().get(pk=slot.pk)
        if locked_slot.responsable_assignments.filter(status=ResponsibleAssignment.Status.ACTIVE).exists():
            release_slot_responsibility(
                actor=actor,
                slot=locked_slot,
                user=locked_slot.current_responsable,
                reason="admin_reassigned_responsable",
            )
        assignment = ResponsibleAssignment.objects.create(
            slot=locked_slot,
            user=user,
            assigned_by_user=actor,
        )
        record_event(
            actor=actor,
            action_type="responsable_assignment_taken",
            target_type="responsible_assignment",
            target_id=assignment.pk,
            occurrence=locked_slot.occurrence,
            slot=locked_slot,
            responsible_assignment=assignment,
            reason="admin_manual_assign",
            metadata={"slot_id": locked_slot.pk, "user_id": user.pk},
        )
        return assignment


def revoke_future_responsable_assignments(*, actor, user, reason="responsable_accreditation_revoked"):
    today = timezone.localdate()
    current_time = timezone.localtime().time()
    assignments = (
        ResponsibleAssignment.objects.select_related("slot", "slot__occurrence")
        .filter(user=user, status=ResponsibleAssignment.Status.ACTIVE)
        .filter(_future_slot_filter(today=today, current_time=current_time, prefix="slot__"))
    )
    count = 0
    for assignment in assignments:
        release_slot_responsibility(actor=actor, slot=assignment.slot, user=user, reason=reason)
        count += 1
    return count


def get_notification_sender_summary():
    sender_email = getattr(settings, "NOTIFICATION_SENDER_EMAIL", "")
    return {
        "sender_email": sender_email,
        "notifications_enabled": bool(sender_email),
    }


def get_email_automation_settings():
    settings_obj, _ = EmailAutomationSettings.objects.get_or_create(pk=1)
    return settings_obj


class _SafeFormatDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def _build_slot_template_context(slot):
    return _SafeFormatDict(
        {
            "session_label": slot.occurrence.label,
            "session_date": slot.occurrence.session_date,
            "slot_start": slot.start_time,
            "slot_end": slot.end_time,
            "slot_index": slot.sequence_index,
        }
    )


def _render_email_template(template, *, slot):
    return template.format_map(_build_slot_template_context(slot))


def _send_reminder_for_slot(slot):
    from accounts.models import User
    automation_settings = get_email_automation_settings()

    recipients = list(
        User.objects.filter(is_active=True)
        .filter(Q(is_responsable_accredited=True) | Q(role=User.Role.ADMIN))
        .values_list("email", flat=True)
    )
    if not recipients:
        return 0
    sender = getattr(settings, "NOTIFICATION_SENDER_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")
    if not sender:
        return 0
    send_mail(
        subject=_render_email_template(automation_settings.reminder_email_subject, slot=slot),
        message=_render_email_template(automation_settings.reminder_email_body, slot=slot),
        from_email=sender,
        recipient_list=recipients,
        fail_silently=False,
    )
    slot.reminder_sent_at = timezone.now()
    slot.save(update_fields=["reminder_sent_at", "updated_at"])
    record_event(
        actor=None,
        action_type="slot_reminder_sent",
        target_type="session_slot",
        target_id=slot.pk,
        occurrence=slot.occurrence,
        slot=slot,
        metadata={"recipient_count": len(recipients)},
    )
    return len(recipients)


def _send_cancellation_notice_for_slot(slot):
    automation_settings = get_email_automation_settings()
    reservations = list(
        slot.occurrence.reservations.active().select_related("user", "occurrence")
    )
    if not reservations:
        return 0
    sender = getattr(settings, "NOTIFICATION_SENDER_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")
    if not sender:
        return 0
    recipients = [reservation.user.email for reservation in reservations]
    send_mail(
        subject=_render_email_template(automation_settings.cancellation_email_subject, slot=slot),
        message=_render_email_template(automation_settings.cancellation_email_body, slot=slot),
        from_email=sender,
        recipient_list=recipients,
        fail_silently=False,
    )
    record_event(
        actor=None,
        action_type="slot_cancellation_notice_sent",
        target_type="session_slot",
        target_id=slot.pk,
        occurrence=slot.occurrence,
        slot=slot,
        metadata={"recipient_count": len(recipients)},
    )
    return len(recipients)


def process_slot_coverage_deadlines(*, today=None):
    reference_date = today or timezone.localdate()
    automation_settings = get_email_automation_settings()
    slots = (
        SessionSlot.objects.select_related("occurrence")
        .prefetch_related(
            Prefetch(
                "responsable_assignments",
                queryset=ResponsibleAssignment.objects.filter(status=ResponsibleAssignment.Status.ACTIVE),
            ),
            Prefetch(
                "reservations",
                queryset=Reservation.objects.active().select_related("user"),
            ),
        )
        .exclude(status__in=[SessionSlot.Status.CANCELLED, SessionSlot.Status.COMPLETED])
        .order_by("occurrence__session_date", "start_time")
    )
    reminders_sent = 0
    auto_cancelled = 0
    notices_sent = 0
    for slot in slots:
        if slot.current_responsable_assignment is not None:
            continue
        days_until = (slot.occurrence.session_date - reference_date).days
        if days_until == automation_settings.reminder_days_before and slot.reminder_sent_at is None:
            reminders_sent += _send_reminder_for_slot(slot)
        if days_until <= automation_settings.cancellation_days_before and slot.status != SessionSlot.Status.CANCELLED:
            change_slot_status(
                actor=None,
                slot=slot,
                status=SessionSlot.Status.CANCELLED,
                reason="auto_cancelled_uncovered",
                automatic=True,
            )
            auto_cancelled += 1
            notices_sent += _send_cancellation_notice_for_slot(slot)
    return {
        "reminders_sent": reminders_sent,
        "slots_auto_cancelled": auto_cancelled,
        "cancellation_notices_sent": notices_sent,
    }

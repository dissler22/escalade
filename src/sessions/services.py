import datetime as dt
import unicodedata
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
    CourseEnrollment,
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


def _build_hour_markers() -> list[dict[str, float | str]]:
    """Markers horaires (toutes les heures) pour l'échelle verticale du calendrier."""
    visible_start_m = VISIBLE_DAY_START.hour * 60 + VISIBLE_DAY_START.minute
    total_range = VISIBLE_RANGE_MINUTES or 1

    markers: list[dict[str, float | str]] = []
    start_hour = VISIBLE_DAY_START.hour
    end_hour = VISIBLE_DAY_END.hour
    for hour in range(start_hour, end_hour + 1):
        minute_of_day = hour * 60
        top_pct = (minute_of_day - visible_start_m) / total_range * 100
        if 0 <= top_pct <= 100:
            markers.append({"top_pct": float(top_pct), "label": f"{hour:02d}:00"})
    return markers


@dataclass(slots=True)
class CalendarOccurrenceBlock:
    occurrence: SessionOccurrence
    occurrence_id: int
    display_label_short: str
    session_type: str
    session_type_label: str
    session_type_class: str
    teacher_name: str
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
    overlapping_count: int
    lane: int = 0
    lane_count: int = 1
    top_pct: float = 0.0
    height_pct: float = 0.0
    background_style: str = ""


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
    session_type: str
    session_type_label: str
    title: str
    date_label: str
    time_label: str
    status_label: str
    status_class: str
    remaining_capacity_label: str
    coverage_summary_label: str
    notes: str
    teacher_name: str
    my_reservation: Reservation | None
    attendee_rows: list[dict[str, int | str]]
    slot_cards: list[InlineSlotCard]
    can_reserve: bool
    can_cancel: bool
    can_edit_as_teacher: bool
    teacher_edit_url: str
    reserve_denial_reason: str
    show_responsibility_section: bool
    week_start_iso: str


@dataclass(slots=True)
class OccurrenceAccessPolicy:
    occurrence: SessionOccurrence
    session_type: str
    can_reserve: bool
    can_cancel: bool
    can_take_responsibility: bool
    can_release_responsibility: bool
    can_edit_as_teacher: bool
    reserve_denial_reason: str


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
        SessionOccurrence.Status.COMPLETED,
    )


def _member_occurrence_queryset(*, start_date=None, end_date=None, today=None, current_time=None):
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
        .select_related("series", "teacher", "series__default_teacher")
        .filter(status__in=_member_calendar_statuses())
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


def _session_type_label(session_type: str) -> str:
    if session_type == SessionSeries.SessionType.COURSE:
        return "Cours"
    return "Pratique libre"


def _session_type_class(session_type: str) -> str:
    return "status-info" if session_type == SessionSeries.SessionType.COURSE else "status-success"


def user_has_course_access(*, user, occurrence: SessionOccurrence) -> bool:
    if not user.is_active:
        return False
    if getattr(user, "is_admin_role", False):
        return True
    series_id = occurrence.series_id
    if series_id is None:
        return False
    enrollments = getattr(user, "_prefetched_active_course_enrollments", None)
    if enrollments is not None:
        return any(enrollment.series_id == series_id for enrollment in enrollments)
    return CourseEnrollment.objects.active().filter(user=user, series_id=series_id).exists()


def can_edit_course_occurrence(*, user, occurrence: SessionOccurrence) -> bool:
    if not user.is_active or occurrence.session_type != SessionSeries.SessionType.COURSE:
        return False
    if getattr(user, "is_admin_role", False):
        return True
    teacher = occurrence.display_teacher
    return teacher is not None and teacher.pk == user.pk


def get_occurrence_access_policy(*, user, occurrence: SessionOccurrence) -> OccurrenceAccessPolicy:
    denial_reason = ""
    can_reserve = False
    if occurrence.is_bookable:
        if occurrence.session_type == SessionSeries.SessionType.FREE_PRACTICE:
            if user.can_book_free_practice:
                can_reserve = True
            else:
                denial_reason = (
                    "Vous n'avez pas de passeport orange pour la pratique libre. "
                    "Pour plus d'info : escalade@usmviroflay.fr"
                )
        elif user_has_course_access(user=user, occurrence=occurrence):
            can_reserve = True
        else:
            denial_reason = (
                "Vous n'êtes pas rattaché à ce cours. "
                "Pour plus d'info : escalade@usmviroflay.fr"
            )
    else:
        if occurrence.status == SessionOccurrence.Status.CANCELLED:
            denial_reason = "Cette seance est annulee."
        elif occurrence.status == SessionOccurrence.Status.COMPLETED:
            denial_reason = "Cette seance est terminee."
        elif occurrence.status != SessionOccurrence.Status.OPEN:
            denial_reason = "Cette seance n est pas ouverte a l inscription."
        elif occurrence.starts_at <= timezone.now():
            denial_reason = "Cette seance a deja commence."
        elif occurrence.remaining_capacity < 1:
            denial_reason = "Cette seance est complete."
    my_reservation = next(
        (reservation for reservation in occurrence.reservations.all() if reservation.user_id == user.id),
        None,
    )
    return OccurrenceAccessPolicy(
        occurrence=occurrence,
        session_type=occurrence.session_type,
        can_reserve=can_reserve and my_reservation is None,
        can_cancel=my_reservation is not None,
        can_take_responsibility=(
            occurrence.session_type == SessionSeries.SessionType.FREE_PRACTICE and user.can_cover_slots
        ),
        can_release_responsibility=(
            occurrence.session_type == SessionSeries.SessionType.FREE_PRACTICE and user.can_cover_slots
        ),
        can_edit_as_teacher=can_edit_course_occurrence(user=user, occurrence=occurrence),
        reserve_denial_reason=denial_reason,
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


def _build_occurrence_background_style(occurrence: SessionOccurrence) -> str:
    if occurrence.status == SessionOccurrence.Status.CANCELLED:
        return ""
    
    if occurrence.is_free_practice:
        slots = list(occurrence.slots.all().order_by("start_time"))
        if not slots:
            return ""
        
        start_m = occurrence.start_time.hour * 60 + occurrence.start_time.minute
        end_m = occurrence.end_time.hour * 60 + occurrence.end_time.minute
        total_duration = max(1, end_m - start_m)
        
        stops = []
        current_m = start_m
        
        for slot in slots:
            slot_start_m = slot.start_time.hour * 60 + slot.start_time.minute
            slot_end_m = slot.end_time.hour * 60 + slot.end_time.minute
            
            # Gap before this slot is considered "intentionally without referent" -> green
            if slot_start_m > current_m:
                gap_start_pct = max(0, min(100, (current_m - start_m) / total_duration * 100))
                gap_end_pct = max(0, min(100, (slot_start_m - start_m) / total_duration * 100))
                stops.append(f"#e0f2e7 {gap_start_pct:.1f}%")
                stops.append(f"#e0f2e7 {gap_end_pct:.1f}%")
            
            actual_start_m = max(current_m, slot_start_m)
            if actual_start_m < slot_end_m:
                start_pct = max(0, min(100, (actual_start_m - start_m) / total_duration * 100))
                end_pct = max(0, min(100, (slot_end_m - start_m) / total_duration * 100))
                
                coverage = _slot_coverage_status(slot)
                if coverage == SessionSlot.CoverageStatus.COVERED:
                    color = "#e0f2e7"  # Green (covered)
                elif coverage == SessionSlot.CoverageStatus.CANCELLED:
                    color = "#f9e2e0"  # Red (cancelled)
                else:
                    color = "#fff9c4"  # Yellow (uncovered)
                    
                stops.append(f"{color} {start_pct:.1f}%")
                stops.append(f"{color} {end_pct:.1f}%")
                
                current_m = slot_end_m
                
        # Gap after the last slot -> green
        if current_m < end_m:
            gap_start_pct = max(0, min(100, (current_m - start_m) / total_duration * 100))
            stops.append(f"#e0f2e7 {gap_start_pct:.1f}%")
            stops.append(f"#e0f2e7 100.0%")
            
        if stops:
            return f"background: linear-gradient(to bottom, {', '.join(stops)});"
        return ""
    
    return ""


def _occurrence_status_summary(occurrence: SessionOccurrence) -> tuple[str, str]:
    remaining_capacity = _occurrence_remaining_capacity(occurrence)
    if occurrence.status == SessionOccurrence.Status.CANCELLED:
        return ("Annulée", "status-danger")
    if occurrence.status == SessionOccurrence.Status.COMPLETED:
        return ("Terminée", "status-neutral")
    if occurrence.status == SessionOccurrence.Status.CLOSED:
        return ("Fermée", "status-warning")
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


def _truncate_calendar_label(label: str) -> str:
    shortened = " ".join((label or "").split())
    if not shortened:
        return "Seance"
    if len(shortened) > 22:
        return f"{shortened[:19].rstrip()}..."
    return shortened


def _normalize_calendar_label(label: str) -> str:
    normalized = unicodedata.normalize("NFKD", label or "")
    ascii_only = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(ascii_only.casefold().split())


def _is_generic_calendar_label(label: str) -> bool:
    normalized = _normalize_calendar_label(label)
    return normalized in {
        "",
        "pratique libre",
        "seance",
        "session",
    }


def _calendar_display_label(occurrence: SessionOccurrence) -> str:
    if not _is_generic_calendar_label(occurrence.label):
        return _shorten_occurrence_label(occurrence.label)
    if occurrence.series is not None and not _is_generic_calendar_label(occurrence.series.label):
        return _shorten_occurrence_label(occurrence.series.label)
    session_type_label = occurrence.get_session_type_display() or occurrence.label or "Seance"
    return _truncate_calendar_label(session_type_label)


def _build_day_blocks(day_occurrences: list[SessionOccurrence], *, selected_occurrence_id: int | None) -> list[CalendarOccurrenceBlock]:
    blocks: list[CalendarOccurrenceBlock] = []
    
    # Pre-sort for lane assignment
    sorted_items = sorted(day_occurrences, key=lambda item: (item.start_time, item.end_time, item.id))
    
    # 1. Basic lane assignment
    lanes_ends: list[dt.time] = []
    temp_blocks: list[dict] = []
    
    for occurrence in sorted_items:
        lane_idx = 0
        found_lane = False
        while lane_idx < len(lanes_ends):
            if lanes_ends[lane_idx] <= occurrence.start_time:
                lanes_ends[lane_idx] = occurrence.end_time
                found_lane = True
                break
            lane_idx += 1
        
        if not found_lane:
            lanes_ends.append(occurrence.end_time)
            lane_idx = len(lanes_ends) - 1
            
        temp_blocks.append({
            "occurrence": occurrence,
            "lane": lane_idx,
        })

    # 2. Group overlaps to find max lanes in each cluster
    # This is simplified: if things overlap in any way, they share a "cluster"
    # and use the max lane count of that cluster.
    # For a real calendar it's more complex, but this should fix most "2 at the same time" issues.
    for i, b1 in enumerate(temp_blocks):
        cluster_lanes = {b1["lane"]}
        # Find all blocks that overlap with b1
        o1 = b1["occurrence"]
        for b2 in temp_blocks:
            o2 = b2["occurrence"]
            if o1.id != o2.id and o1.start_time < o2.end_time and o1.end_time > o2.start_time:
                cluster_lanes.add(b2["lane"])
        b1["lane_count"] = max(cluster_lanes) + 1 if cluster_lanes else 1

    # 3. Final block creation
    visible_start_m = VISIBLE_DAY_START.hour * 60 + VISIBLE_DAY_START.minute
    total_range = VISIBLE_RANGE_MINUTES or 1

    for b in temp_blocks:
        occurrence = b["occurrence"]
        status_label, status_class = _occurrence_status_summary(occurrence)
        coverage_summary = _coverage_summary(occurrence)
        remaining_capacity = _occurrence_remaining_capacity(occurrence)
        
        # Re-calc local overlap for display
        local_overlaps = sum(1 for other in temp_blocks if other["occurrence"].id != occurrence.id and other["occurrence"].start_time < occurrence.end_time and other["occurrence"].end_time > occurrence.start_time)

        # Vertical positioning
        start_m = occurrence.start_time.hour * 60 + occurrence.start_time.minute
        end_m = occurrence.end_time.hour * 60 + occurrence.end_time.minute
        
        # Clamp to visible range
        clamped_start = max(start_m, visible_start_m)
        clamped_end = min(end_m, visible_start_m + total_range)
        
        top_pct = max(0, (clamped_start - visible_start_m) / total_range * 100)
        height_pct = max(5, (clamped_end - clamped_start) / total_range * 100) # Min height 5%
        
        background_style = _build_occurrence_background_style(occurrence)
        
        blocks.append(
            CalendarOccurrenceBlock(
                occurrence=occurrence,
                occurrence_id=occurrence.id,
                display_label_short=_calendar_display_label(occurrence),
                session_type=occurrence.session_type,
                session_type_label=_session_type_label(occurrence.session_type),
                session_type_class=_session_type_class(occurrence.session_type),
                teacher_name=occurrence.display_teacher.full_name if occurrence.display_teacher else "",
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
                covered_slots=coverage_summary["covered"] if occurrence.is_free_practice else 0,
                total_slots=coverage_summary["total"] if occurrence.is_free_practice else 0,
                overlapping_count=local_overlaps,
                lane=b["lane"],
                lane_count=max(b["lane_count"], b["lane"] + 1),
                top_pct=top_pct,
                height_pct=height_pct,
                background_style=background_style,
            )
        )
    return blocks


def _build_inline_detail(*, occurrence: SessionOccurrence, user, week_start: dt.date) -> InlineOccurrenceDetail:
    policy = get_occurrence_access_policy(user=user, occurrence=occurrence)
    my_reservation = next((reservation for reservation in occurrence.reservations.all() if reservation.user_id == user.id), None)
    attendee_rows = [
        {"user_id": reservation.user_id, "full_name": reservation.user.full_name}
        for reservation in occurrence.reservations.all()
    ]
    attendee_rows.sort(key=lambda row: str(row["full_name"]).casefold())
    slot_cards: list[InlineSlotCard] = []
    for slot in occurrence.slots.all() if occurrence.is_free_practice else []:
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
            policy.can_take_responsibility
            and coverage_status == SessionSlot.CoverageStatus.UNCOVERED
            and slot.starts_at > timezone.now()
        )
        can_release = policy.can_release_responsibility and my_assignment is not None and slot.starts_at > timezone.now()
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
        session_type=occurrence.session_type,
        session_type_label=_session_type_label(occurrence.session_type),
        title=occurrence.label,
        date_label=formats.date_format(occurrence.session_date, "l j F"),
        time_label=(
            f"{occurrence.start_time:%H}h{occurrence.start_time:%M} - "
            f"{occurrence.end_time:%H}h{occurrence.end_time:%M}"
        ),
        status_label=status_label,
        status_class=status_class,
        remaining_capacity_label=f"{remaining_capacity} place(s) restante(s)",
        coverage_summary_label=(
            f"{coverage_summary['covered']}/{coverage_summary['total']} creneau(x) avec responsable"
        ),
        notes=occurrence.notes.strip(),
        teacher_name=occurrence.display_teacher.full_name if occurrence.display_teacher else "",
        my_reservation=my_reservation,
        attendee_rows=attendee_rows,
        slot_cards=slot_cards,
        can_reserve=policy.can_reserve,
        can_cancel=my_reservation is not None,
        can_edit_as_teacher=policy.can_edit_as_teacher and not user.is_admin_role,
        teacher_edit_url=reverse("sessions:teacher-occurrence-edit", args=[occurrence.pk])
        if occurrence.is_course
        else "",
        reserve_denial_reason=policy.reserve_denial_reason,
        show_responsibility_section=occurrence.is_free_practice,
        week_start_iso=week_start.isoformat(),
    )


def build_member_calendar_page(*, user, week_start_value=None, selected_occurrence_value=None) -> CalendarPageState:
    week_start = normalize_week_start(week_start_value)
    week_end = week_start + dt.timedelta(days=6)
    user._prefetched_active_course_enrollments = list(
        CourseEnrollment.objects.active().filter(user=user).select_related("series")
    )
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
    # Libellés des jours/mois en français (sans dépendre de la locale du serveur).
    weekday_abbrev_fr = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
    weekday_full_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    month_full_fr = [
        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre",
    ]
    for offset in range(7):
        current_date = week_start + dt.timedelta(days=offset)
        day_occurrences = [occurrence for occurrence in occurrences if occurrence.session_date == current_date]
        days.append(
            CalendarDay(
                date=current_date,
                label_short=weekday_abbrev_fr[current_date.weekday()],
                label_full=f"{weekday_full_fr[current_date.weekday()]} {current_date.day} {month_full_fr[current_date.month - 1]}",
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
        hour_markers=_build_hour_markers(),
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


def occurrence_is_past(*, occurrence: SessionOccurrence, now=None) -> bool:
    if now is None:
        now = timezone.now()
    return occurrence.ends_at <= now


def slot_is_past(*, slot: SessionSlot, now=None) -> bool:
    if now is None:
        now = timezone.now()
    return slot.ends_at <= now


def _get_slot_segments(*, session_date, start_time, end_time):
    start_dt = dt.datetime.combine(session_date, start_time)
    end_dt = dt.datetime.combine(session_date, end_time)
    if end_dt <= start_dt:
        raise ValidationError("L’heure de fin doit être après l’heure de début.")
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
        .select_related("series", "teacher", "series__default_teacher")
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


def create_series(*, actor, cleaned_data, slot_formset=None, weeks=8):
    with transaction.atomic():
        series = SessionSeries.objects.create(created_by=actor, **cleaned_data)
        if slot_formset is not None:
            slot_formset.instance = series
            slot_formset.save()
            if hasattr(series, "_prefetched_objects_cache"):
                series._prefetched_objects_cache.pop("slot_templates", None)
        generate_future_occurrences(series=series, actor=actor, weeks=weeks)
        record_event(
            actor=actor,
            action_type="session_series_created",
            target_type="session_series",
            target_id=series.pk,
            metadata={
                "label": series.label,
                "default_capacity": series.default_capacity,
                "session_type": series.session_type,
                "default_teacher_id": series.default_teacher_id,
            },
        )
        return series


def _build_future_series_dates(*, weekday, count, reference_date=None):
    if reference_date is None:
        reference_date = timezone.localdate()
    target_dates = []
    for offset in range(count):
        day = reference_date + dt.timedelta(days=offset * 7)
        target_date = day + dt.timedelta((weekday - day.weekday()) % 7)
        target_dates.append(target_date)
    return target_dates


def _build_temporary_series_dates(*, current_dates, target_dates):
    anchor_date = max([timezone.localdate(), *current_dates, *target_dates]) + dt.timedelta(days=400)
    return [anchor_date + dt.timedelta(days=index) for index in range(len(current_dates))]


def update_series(*, actor, series, cleaned_data, slot_formset=None):
    previous_session_type = series.session_type
    previous_default_teacher_id = series.default_teacher_id
    previous_weekday = series.weekday
    for field, value in cleaned_data.items():
        setattr(series, field, value)
    series.full_clean()
    with transaction.atomic():
        series.save()
        if slot_formset is not None:
            slot_formset.instance = series
            slot_formset.save()
            if hasattr(series, "_prefetched_objects_cache"):
                series._prefetched_objects_cache.pop("slot_templates", None)
        
        occurrences = list(series.occurrences.all().order_by("session_date", "id"))
        target_dates = _build_future_series_dates(
            weekday=series.weekday,
            count=len(occurrences),
        )
        temporary_dates = _build_temporary_series_dates(
            current_dates=[occurrence.session_date for occurrence in occurrences],
            target_dates=target_dates,
        )
        for occurrence, temporary_date in zip(occurrences, temporary_dates, strict=True):
            occurrence.session_date = temporary_date
            occurrence.save(update_fields=["session_date", "updated_at"])
        for occurrence, target_date in zip(occurrences, target_dates, strict=True):
            occurrence.label = series.label
            occurrence.session_date = target_date
            occurrence.start_time = series.start_time
            occurrence.end_time = series.end_time
            occurrence.capacity = series.default_capacity
            occurrence.session_type = series.session_type
            if series.session_type == SessionSeries.SessionType.COURSE:
                if occurrence.teacher_id in {None, previous_default_teacher_id}:
                    occurrence.teacher = series.default_teacher
            elif occurrence.teacher_id == previous_default_teacher_id:
                occurrence.teacher = None
            occurrence.full_clean()
            occurrence.save()
            sync_occurrence_slots(actor=actor, occurrence=occurrence)
            record_event(
                actor=actor,
                action_type="session_series_updated",
                target_type="session_series",
                target_id=series.pk,
                metadata={
                    "label": series.label,
                    "weekday": series.weekday,
                    "default_capacity": series.default_capacity,
                    "session_type": series.session_type,
                    "default_teacher_id": series.default_teacher_id,
                    "previous_weekday": previous_weekday,
                    "previous_session_type": previous_session_type,
                },
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
                "session_type": series.session_type,
                "teacher": series.default_teacher,
                "status": SessionOccurrence.Status.OPEN,
                "created_by": actor,
            },
        )
        if was_created:
            sync_occurrence_slots(actor=actor, occurrence=occurrence)
            created.append(occurrence)
    return created


def sync_occurrence_slots(*, actor, occurrence, create_defaults_if_empty=True):
    if occurrence.is_course:
        if occurrence.slots.exists():
            occurrence.slots.all().delete()
        return []
        
    if occurrence.series and occurrence.series.slot_templates.exists():
        expected_segments = [
            {
                "sequence_index": template.sequence_index,
                "start_time": template.start_time,
                "end_time": template.end_time,
            }
            for template in occurrence.series.slot_templates.all()
        ]
    else:
        expected_segments = _get_slot_segments(
            session_date=occurrence.session_date,
            start_time=occurrence.start_time,
            end_time=occurrence.end_time,
        )

    existing_slots = list(occurrence.slots.order_by("sequence_index"))
    
    if existing_slots:
        matches = len(existing_slots) == len(expected_segments)
        if matches:
            for slot, segment in zip(existing_slots, expected_segments):
                if slot.start_time != segment["start_time"] or slot.end_time != segment["end_time"]:
                    matches = False
                    break
        
        if not matches:
            has_commitments = any(_slot_has_commitments(s) for s in existing_slots)
            if not has_commitments:
                occurrence.slots.all().delete()
                existing_slots = []

    if not existing_slots and create_defaults_if_empty:
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
    for index, slot in enumerate(existing_slots, start=1):
        active_count = slot.reservations.active().count()
        if occurrence.capacity < active_count:
            raise ValidationError("La capacite ne peut pas etre inferieure aux reservations actives d un creneau.")
        changed = False
        if slot.sequence_index != index:
            slot.sequence_index = index
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
        if cleaned_data.get("series") is not None:
            cleaned_data["session_type"] = cleaned_data["series"].session_type
            if cleaned_data["session_type"] == SessionSeries.SessionType.COURSE and cleaned_data.get("teacher") is None:
                cleaned_data["teacher"] = cleaned_data["series"].default_teacher
        if cleaned_data.get("session_type") == SessionSeries.SessionType.FREE_PRACTICE:
            cleaned_data["teacher"] = None
        occurrence = SessionOccurrence.objects.create(created_by=actor, **cleaned_data)
        sync_occurrence_slots(actor=actor, occurrence=occurrence, create_defaults_if_empty=True)
        record_event(
            actor=actor,
            action_type="session_occurrence_created",
            target_type="session_occurrence",
            target_id=occurrence.pk,
            occurrence=occurrence,
            metadata={
                "label": occurrence.label,
                "capacity": occurrence.capacity,
                "status": occurrence.status,
                "session_type": occurrence.session_type,
                "teacher_id": occurrence.teacher_id,
            },
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
    if occurrence.series is not None:
        occurrence.session_type = occurrence.series.session_type
        if occurrence.is_course and occurrence.teacher_id is None:
            occurrence.teacher = occurrence.series.default_teacher
    if occurrence.is_free_practice:
        occurrence.teacher = None
    if mark_override:
        occurrence.is_override = True
    occurrence.full_clean()
    with transaction.atomic():
        occurrence.save()
        sync_occurrence_slots(actor=actor, occurrence=occurrence, create_defaults_if_empty=False)
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
                "session_type": occurrence.session_type,
                "teacher_id": occurrence.teacher_id,
            },
        )
    return occurrence


def update_occurrence_as_teacher(*, actor, occurrence, cleaned_data):
    if not can_edit_course_occurrence(user=actor, occurrence=occurrence):
        raise ValidationError("Vous ne pouvez modifier que vos propres occurrences de cours.")
    if occurrence.is_free_practice:
        raise ValidationError("Cette occurrence n est pas un cours.")
    if occurrence_is_past(occurrence=occurrence):
        raise ValidationError("Impossible de modifier une occurrence passée.")

    for forbidden_field in ("series", "session_type", "teacher"):
        cleaned_data.pop(forbidden_field, None)
    for field, value in cleaned_data.items():
        setattr(occurrence, field, value)
    occurrence.is_override = True
    occurrence.full_clean()
    with transaction.atomic():
        occurrence.save()
        record_event(
            actor=actor,
            action_type="course_occurrence_updated_by_teacher",
            target_type="session_occurrence",
            target_id=occurrence.pk,
            occurrence=occurrence,
            metadata={
                "capacity": occurrence.capacity,
                "status": occurrence.status,
                "teacher_id": occurrence.teacher_id,
                "series_id": occurrence.series_id,
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
            if occurrence.is_course:
                break
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
    if slot.occurrence.is_course:
        raise ValidationError("Les cours n utilisent pas de creneaux responsables.")

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
    if slot.occurrence.is_course:
        raise ValidationError("Les cours n utilisent pas de creneaux responsables.")
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


def delete_slot(*, actor, slot):
    occurrence = slot.occurrence
    slot_id = slot.pk
    with transaction.atomic():
        slot.delete()
        remaining_slots = list(occurrence.slots.order_by("sequence_index", "id"))
        for index, remaining_slot in enumerate(remaining_slots, start=1):
            if remaining_slot.sequence_index != index:
                remaining_slot.sequence_index = index
                remaining_slot.save(update_fields=["sequence_index"])
        record_event(
            actor=actor,
            action_type="slot_deleted",
            target_type="session_slot",
            target_id=slot_id,
            occurrence=occurrence,
            metadata={"occurrence_id": occurrence.pk},
        )


def _validate_responsable_assignment(*, user, slot):
    if slot.occurrence.is_course:
        raise ValidationError("La couverture responsable est reservee aux pratiques libres.")
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
    if slot.occurrence.is_course:
        raise ValidationError("La couverture responsable est reservee aux pratiques libres.")
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

    if slot.occurrence.is_course:
        return 0
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
    if slot.occurrence.is_course:
        return 0
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
        .filter(occurrence__session_type=SessionSeries.SessionType.FREE_PRACTICE)
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

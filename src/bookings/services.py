from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from audit.services import record_event
from sessions.models import SessionOccurrence
from sessions.services import get_occurrence_access_policy

from .models import Reservation


def _validate_member_booking(user, occurrence, *, allow_closed_admin=False):
    if occurrence.status == SessionOccurrence.Status.CANCELLED:
        raise ValidationError("La seance est annulee.")
    if occurrence.status == SessionOccurrence.Status.COMPLETED:
        raise ValidationError("La seance est terminee.")
    if not allow_closed_admin and occurrence.status != SessionOccurrence.Status.OPEN:
        raise ValidationError("La seance n'est pas ouverte a la reservation.")
    if occurrence.starts_at <= timezone.now():
        raise ValidationError("La seance a deja commence.")
    if Reservation.objects.active().filter(occurrence=occurrence, user=user).exists():
        raise ValidationError("Vous etes deja inscrit a cette seance.")
    if occurrence.remaining_capacity < 1:
        raise ValidationError("La seance est complete.")
    if not allow_closed_admin:
        policy = get_occurrence_access_policy(user=user, occurrence=occurrence)
        if not policy.can_reserve:
            raise ValidationError(policy.reserve_denial_reason or "Vous n etes pas autorise a vous inscrire a cette seance.")


def _create_booking(*, actor, user, occurrence, action_type, reason=""):
    with transaction.atomic():
        locked_occurrence = SessionOccurrence.objects.select_for_update().get(pk=occurrence.pk)
        _validate_member_booking(
            user,
            locked_occurrence,
            allow_closed_admin=actor.is_admin_role,
        )
        reservation = Reservation.objects.create(
            occurrence=locked_occurrence,
            user=user,
            created_by_role=actor.role,
        )
        record_event(
            actor=actor,
            action_type=action_type,
            target_type="reservation",
            target_id=reservation.pk,
            occurrence=locked_occurrence,
            reason=reason,
            metadata={"remaining_capacity": locked_occurrence.remaining_capacity, "member_id": user.pk},
        )
        return reservation


def create_member_booking(*, user, occurrence):
    return _create_booking(
        actor=user,
        user=user,
        occurrence=occurrence,
        action_type="reservation_created",
    )


def _cancel_booking(*, actor, user, occurrence, action_type, reason):
    with transaction.atomic():
        reservation = Reservation.objects.select_for_update().active().get(occurrence=occurrence, user=user)
        if occurrence.starts_at <= timezone.now():
            raise ValidationError("Impossible d'annuler une seance deja commencee.")
        reservation.status = Reservation.Status.CANCELLED
        reservation.cancelled_at = timezone.now()
        reservation.cancellation_reason = reason
        reservation.save(update_fields=["status", "cancelled_at", "cancellation_reason"])
        record_event(
            actor=actor,
            action_type=action_type,
            target_type="reservation",
            target_id=reservation.pk,
            occurrence=occurrence,
            reason=reason,
            metadata={"remaining_capacity": occurrence.remaining_capacity, "member_id": user.pk},
        )
        return reservation


def cancel_member_booking(*, user, occurrence):
    return _cancel_booking(
        actor=user,
        user=user,
        occurrence=occurrence,
        action_type="reservation_cancelled",
        reason="member_cancelled",
    )


def add_manual_booking(*, actor, occurrence, user, reason="admin_manual_add"):
    return _create_booking(
        actor=actor,
        user=user,
        occurrence=occurrence,
        action_type="reservation_added_manually",
        reason=reason,
    )


def remove_manual_booking(*, actor, occurrence, user, reason="admin_manual_remove"):
    return _cancel_booking(
        actor=actor,
        user=user,
        occurrence=occurrence,
        action_type="reservation_removed_manually",
        reason=reason,
    )

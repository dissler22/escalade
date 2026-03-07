from audit.models import AuditEntry


def record_event(
    *,
    actor,
    action_type,
    target_type,
    target_id,
    occurrence=None,
    reservation=None,
    reason="",
    metadata=None,
):
    actor_role = ""
    if actor is not None:
        actor_role = getattr(actor, "role", "") or ("admin" if actor.is_superuser else "member")
    return AuditEntry.objects.create(
        actor_user=actor,
        actor_role_snapshot=actor_role,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        occurrence=occurrence,
        reservation=reservation,
        reason=reason,
        metadata_snapshot=metadata or {},
    )


def get_occurrence_history(occurrence):
    return occurrence.audit_entries.select_related("actor_user", "reservation")

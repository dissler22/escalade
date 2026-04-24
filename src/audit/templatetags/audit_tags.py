from django import template

register = template.Library()

_STATUS_FR = {
    "draft": "brouillon",
    "open": "ouvert",
    "closed": "fermé",
    "cancelled": "annulé",
    "completed": "terminé",
}

_ACTION_LABELS = {
    "session_series_created": "Série créée",
    "session_series_updated": "Série mise à jour",
    "slot_created": "Créneau créé",
    "slot_updated": "Créneau mis à jour",
    "slot_deleted": "Créneau supprimé",
    "session_occurrence_created": "Séance créée",
    "session_occurrence_updated": "Séance mise à jour",
    "course_occurrence_updated_by_teacher": "Occurrence de cours modifiée (enseignant)",
    "slot_auto_cancelled_uncovered": "Créneau annulé automatiquement (sans responsable)",
    "responsable_assignment_taken": "Responsable positionné",
    "responsable_assignment_revoked": "Responsable retiré",
    "slot_reminder_sent": "Rappel envoyé",
    "slot_cancellation_notice_sent": "Avis d’annulation envoyé",
    "reservation_created": "Réservation créée",
    "reservation_cancelled": "Réservation annulée",
    "reservation_added_manually": "Inscription ajoutée manuellement",
    "reservation_removed_manually": "Inscription retirée manuellement",
    "course_enrollment_assigned": "Inscription au cours enregistrée",
    "course_enrollment_removed": "Inscription au cours retirée",
    "account_created": "Compte créé",
    "account_updated": "Compte mis à jour",
    "account_password_reset": "Code d’accès réinitialisé",
    "responsable_accreditation_granted": "Accréditation référent accordée",
    "responsable_accreditation_revoked": "Accréditation référent retirée",
    "orange_passport_granted": "Passport orange accordé",
    "orange_passport_revoked": "Passport orange retiré",
    "teaching_capability_updated": "Habilitation enseignement mise à jour",
}


@register.filter
def audit_action_label(action_type: str) -> str:
    if not action_type:
        return "—"
    if action_type in _ACTION_LABELS:
        return _ACTION_LABELS[action_type]
    if action_type.startswith("slot_"):
        suffix = action_type[5:]
        if suffix in _STATUS_FR:
            return f"Créneau {_STATUS_FR[suffix]}"
    if action_type.startswith("session_occurrence_"):
        suffix = action_type[len("session_occurrence_") :]
        if suffix in _STATUS_FR:
            return f"Séance {_STATUS_FR[suffix]}"
    return action_type.replace("_", " ")

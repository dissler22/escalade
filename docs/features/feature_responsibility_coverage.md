# Feature: responsibility-coverage

## Purpose
- Assurer qu'un creneau de pratique libre est couvert par au plus un responsable actif.
- Exposer les actions membre de prise/liberation de responsabilite.
- Permettre l'affectation/retrait manuel admin sur les creneaux a venir.

## Source Files
- `src/sessions/models.py` (`SessionSlot`, `ResponsibleAssignment`)
- `src/sessions/services.py` (`take_slot_responsibility`, `release_slot_responsibility`, `assign_slot_responsibility`, `revoke_future_responsable_assignments`)
- `src/sessions/views.py`
- `src/sessions/views_admin.py`
- `src/accounts/views_admin.py` (bascule accreditation responsable)
- `tests/unit/test_slot_responsibility_service.py`
- `tests/integration/test_member_responsable_flow.py`
- `tests/integration/test_admin_responsable_management.py`

## Public Contracts
- Routes membre:
  - `POST /sessions/slots/<slot_id>/responsibility/take/`
  - `POST /sessions/slots/<slot_id>/responsibility/release/`
- Routes admin:
  - `POST /admin/sessions/slots/<slot_id>/responsable/assign/`
  - `POST /admin/sessions/slots/<slot_id>/responsable/release/`
  - `POST /admin/accounts/<user_id>/status/` (impact accreditation)
- Regles metier:
  - unicite responsable actif par creneau (`unique_active_responsable_per_slot`)
  - couverture autorisee uniquement sur `free_practice`
  - interdite sur creneau annule, termine, ou deja commence
  - reaffectation admin = revocation de l'actif precedent puis creation de la nouvelle affectation
  - retrait accreditation responsable revoque les affectations futures de l'utilisateur

## Dependencies
- Depend de `feature_identity_and_access` pour les attributs `can_cover_slots`.
- Depend de `feature_session_planning_and_calendar` pour les creneaux et leur statut.
- Depend de `feature_audit_and_operations` pour la tracabilite `responsable_assignment_*`.

## Validation
- `.venv/bin/python -m pytest tests/unit/test_slot_responsibility_service.py`
- `.venv/bin/python -m pytest tests/integration/test_member_responsable_flow.py`
- `.venv/bin/python -m pytest tests/integration/test_admin_responsable_management.py`

## Drift / Limits
- La couverture ne traite pas la planification optimale; elle gere l'affectation unitaire par creneau.
- Pas de mecanisme de candidature ou file d'attente de responsables.

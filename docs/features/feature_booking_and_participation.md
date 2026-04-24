# Feature: booking-and-participation

## Purpose
- Gerer l'inscription et la desinscription des membres aux occurrences.
- Exposer la page `Mes reservations` et les actions reserve/cancel depuis le calendrier.
- Permettre les corrections admin d'inscriptions quand une situation operationnelle l'exige.

## Source Files
- `src/bookings/models.py`
- `src/bookings/services.py`
- `src/bookings/views.py`
- `src/bookings/views_admin.py`
- `src/bookings/urls.py`
- `src/bookings/urls_admin.py`
- `src/templates/bookings/my_reservations.html`
- `src/templates/admin/bookings/session_reservations.html`
- `tests/integration/test_member_booking_flow.py`
- `tests/integration/test_admin_booking_corrections.py`
- `tests/unit/test_booking_service.py`

## Public Contracts
- Routes membre:
  - `GET /bookings/mine/`
  - `POST /bookings/<occurrence_id>/reserve/`
  - `POST /bookings/<occurrence_id>/cancel/`
- Routes admin corrections:
  - `GET /admin/bookings/sessions/<occurrence_id>/`
  - `POST /admin/bookings/sessions/<occurrence_id>/add/`
  - `POST /admin/bookings/sessions/<occurrence_id>/remove/<user_id>/`
- Regles metier:
  - unicite reservation active par `(occurrence, user)`
  - refus si occurrence annulee/terminee/deja commencee/complete/deja reservee
  - verification des droits de reservation via policy d'acces occurrence
  - ajout manuel admin possible pour occurrence future, meme fermee, mais jamais en depassement capacite
  - desinscription refusee pour une occurrence deja commencee

## Dependencies
- Depend de `feature_identity_and_access` pour les droits utilisateur.
- Depend de `feature_session_planning_and_calendar` pour les occurrences et contextes de retour calendrier.
- Depend de `feature_audit_and_operations` pour les evenements `reservation_*`.

## Validation
- `.venv/bin/python -m pytest tests/unit/test_booking_service.py`
- `.venv/bin/python -m pytest tests/integration/test_member_booking_flow.py`
- `.venv/bin/python -m pytest tests/integration/test_admin_booking_corrections.py`

## Drift / Limits
- Pas de liste d'attente.
- Le modele conserve aussi une reference `slot` legacy, non utilisee dans le flux nominal actuel.
- Les corrections admin restent soumises aux contraintes temporelles et de capacite.

# Feature: session-planning-and-calendar

## Purpose
- Porter le modele des seances: series, occurrences, creneaux, types `free_practice` et `course`.
- Offrir la vue membre hebdomadaire (8h-23h) avec detail inline et navigation semaine.
- Fournir les ecrans admin de pilotage des series/occurrences/creneaux.

## Source Files
- `src/sessions/models.py`
- `src/sessions/forms.py`
- `src/sessions/services.py`
- `src/sessions/views.py`
- `src/sessions/views_admin.py`
- `src/sessions/urls.py`
- `src/sessions/urls_admin.py`
- `src/templates/sessions/session_list.html`
- `src/templates/sessions/_calendar_grid.html`
- `src/templates/sessions/_calendar_detail.html`
- `src/templates/admin/sessions/series_list.html`
- `src/templates/admin/sessions/series_form.html`
- `src/templates/admin/sessions/occurrence_form.html`
- `tests/integration/test_admin_session_management.py`
- `tests/integration/test_session_access_types.py`
- `tests/unit/test_session_slot_generation.py`

## Public Contracts
- Routes membre:
  - `GET /sessions/?week_start=<YYYY-MM-DD>&selected_occurrence=<id>`
  - `GET /sessions/<occurrence_id>/` (redirige vers calendrier pour occurrence future)
  - `GET|POST /sessions/teaching/<occurrence_id>/edit/` (edition prof sur occurrence de cours autorisee)
- Routes admin planning:
  - `GET /admin/sessions/`
  - `GET|POST /admin/sessions/series/new/`
  - `GET|POST /admin/sessions/series/<series_id>/edit/`
  - `POST /admin/sessions/series/<series_id>/delete/`
  - `GET|POST /admin/sessions/occurrences/new/`
  - `GET|POST /admin/sessions/occurrences/<occurrence_id>/edit/`
  - `POST /admin/sessions/occurrences/<occurrence_id>/status/`
  - `POST /admin/sessions/occurrences/<occurrence_id>/delete/`
  - `POST /admin/sessions/slots/<slot_id>/edit|status|delete/`
- Regles de structure:
  - une occurrence `course` n'utilise pas de creneaux responsables
  - une occurrence `free_practice` cree/synchronise des creneaux selon templates de serie ou segmentation max 90 min
  - les occurrences/slots passes sont en lecture seule pour les actions directes d'edition/statut/suppression

## Dependencies
- Depend de `feature_identity_and_access` pour la selection prof et les droits d'acces.
- Depend de `feature_booking_and_participation` pour le calcul capacite/restant et actions du detail inline.
- Depend de `feature_responsibility_coverage` pour les etats de couverture des creneaux.
- Depend de `feature_audit_and_operations` pour l'historique des changements planning.

## Validation
- `.venv/bin/python -m pytest tests/integration/test_admin_session_management.py`
- `.venv/bin/python -m pytest tests/integration/test_session_access_types.py`
- `.venv/bin/python -m pytest tests/unit/test_session_slot_generation.py`

## Drift / Limits
- La plage horaire visible du calendrier est fixe (08:00-23:00).
- Le calcul visuel des chevauchements est volontairement simple et optimise pour les cas usuels.
- Les statuts membres affiches en calendrier excluent les occurrences `draft`.
- Les operations au niveau serie peuvent encore impacter des occurrences historiques, car la protection "passe" vise surtout les actions directes sur occurrence/slot.

# Feature: notifications-and-deadlines

## Purpose
- Parametrer les delais et templates email lies a la couverture des creneaux.
- Executer les rappels et auto-annulations sur creneaux non couverts.
- Rendre ce traitement rejouable via une commande de management.

## Source Files
- `src/sessions/models.py` (`EmailAutomationSettings`)
- `src/sessions/forms.py` (`EmailAutomationSettingsForm`)
- `src/sessions/services.py` (`process_slot_coverage_deadlines` + helpers email)
- `src/sessions/management/commands/process_slot_coverage_deadlines.py`
- `src/accounts/views_admin.py` (`email_automation`)
- `src/templates/admin/accounts/email_automation.html`
- `tests/unit/test_slot_coverage_deadlines.py`
- `tests/integration/test_slot_notification_flow.py`

## Public Contracts
- Route admin parametres:
  - `GET|POST /admin/accounts/email-automation/`
- Commande batch:
  - `python manage.py process_slot_coverage_deadlines`
- Regles de traitement:
  - rappel envoye quand `days_until == reminder_days_before` et pas encore envoye
  - auto-annulation quand `days_until <= cancellation_days_before`
  - creneaux deja couverts, annules, termines, ou de type `course` exclus du traitement
  - emission email conditionnee a la presence d'un expediteur configure

## Dependencies
- Depend de `feature_responsibility_coverage` pour l'etat de couverture des creneaux.
- Depend de `feature_identity_and_access` pour la population cible des rappels (admin + responsables accredites actifs).
- Depend de `feature_audit_and_operations` pour les evenements `slot_reminder_sent`, `slot_auto_cancelled_uncovered`, `slot_cancellation_notice_sent`.
- Depend de la configuration runtime email (`APP_NOTIFICATION_SENDER_EMAIL` / SMTP).

## Validation
- `.venv/bin/python -m pytest tests/unit/test_slot_coverage_deadlines.py`
- `.venv/bin/python -m pytest tests/integration/test_slot_notification_flow.py`

## Drift / Limits
- Le traitement est synchrone; pas de queue asynchrone.
- Le mail d'annulation cible toutes les reservations actives de l'occurrence, pas un sous-ensemble par creneau.
- Les valeurs "J-7/J-2" sont un parametrage par defaut, pas une constante immuable.
- Le batch ne filtre pas explicitement les creneaux deja passes s'ils restent en statut ouvert; ils peuvent donc etre rattrapes par la regle `days_until <= cancellation_days_before`.

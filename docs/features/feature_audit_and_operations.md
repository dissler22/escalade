# Feature: audit-and-operations

## Purpose
- Centraliser la tracabilite des evenements metier critiques de l'application.
- Exposer l'historique d'une seance pour investigation et reprise manuelle.
- Encadrer l'exploitation runtime/deploiement/rollback sur VM.

## Source Files
- `src/audit/models.py`
- `src/audit/services.py`
- `src/audit/views.py`
- `src/audit/urls.py`
- `src/templates/admin/audit/session_history.html`
- `src/config/settings.py`
- `src/config/env.py`
- `.env.example`
- `scripts/deploy/common.sh`
- `scripts/deploy/provision_vm.sh`
- `scripts/deploy/first_release.sh`
- `scripts/deploy/release.sh`
- `scripts/deploy/backup_sqlite.sh`
- `scripts/deploy/restore_sqlite.sh`
- `scripts/deploy/rollback.sh`
- `scripts/deploy/smoke_check.sh`
- `docs/deployment.md`
- `docs/operations.md`
- `docs/deploy/README.md`
- `docs/deploy/nginx/escalade.conf`
- `docs/deploy/systemd/escalade.service`
- `tests/unit/test_audit_service.py`
- `tests/unit/test_settings_runtime.py`

## Public Contracts
- Route historique admin:
  - `GET /admin/audit/sessions/<occurrence_id>/`
  - acces reserve aux comptes admin
- Contrat d'audit:
  - `record_event(...)` persiste `action_type`, acteur, cible, contexte (occurrence/slot/reservation/assignment), raison, metadata
- Contrat ops/deploiement:
  - layout runtime sous `/srv/escalade/{releases,current,shared}`
  - scripts de cycle de vie: provision, release, backup, restore, rollback, smoke check
  - configuration externalisee par variables d'environnement

## Dependencies
- Consomme les evenements emis par `feature_identity_and_access`, `feature_session_planning_and_calendar`, `feature_booking_and_participation`, `feature_responsibility_coverage`, `feature_notifications_and_deadlines`.
- Depend de l'environnement systeme cible (`systemd`, `nginx`, `python3`, `sqlite3`, `curl`).

## Validation
- `.venv/bin/python -m pytest tests/unit/test_audit_service.py`
- `.venv/bin/python -m pytest tests/unit/test_settings_runtime.py`
- `.venv/bin/python -m pytest tests/contract/test_openapi_contract.py`

## Drift / Limits
- Le catalogue `action_type` est base sur des chaines, sans enum globale centralisee.
- La retention d'audit et de logs depend surtout des pratiques operationnelles documentees.
- Architecture de production mono-VM SQLite: robuste pour petit volume, limitee en scalabilite horizontale.

# Feature: identity-and-access

## Purpose
- Gerer l'identite applicative des utilisateurs (compte, role, statuts de droit).
- Fournir les parcours d'acces: login nom/prenom/code, cycle de mot de passe temporaire, logout.
- Permettre l'administration des comptes: creation, mise a jour des droits, reset code, import roster.

## Source Files
- `src/accounts/models.py`
- `src/accounts/auth_backends.py`
- `src/accounts/forms.py`
- `src/accounts/views.py`
- `src/accounts/views_admin.py`
- `src/accounts/importers.py`
- `src/accounts/identity.py`
- `src/accounts/middleware.py`
- `src/accounts/urls.py`
- `src/accounts/urls_admin.py`
- `tests/integration/test_accounts_access.py`
- `tests/integration/test_admin_permissions.py`
- `tests/integration/test_admin_responsable_management.py`

## Public Contracts
- Routes publiques et membre:
  - `GET /`
  - `GET|POST /login/`
  - `GET|POST /password/`
  - `GET|POST /logout/`
- Routes admin comptes:
  - `GET /admin/accounts/`
  - `POST /admin/accounts/create/`
  - `POST /admin/accounts/import/`
  - `POST /admin/accounts/<user_id>/status/`
  - `POST /admin/accounts/<user_id>/reset-password/`
- Regles d'acces:
  - authentification par `first_name + last_name + password` (pas par email)
  - login refuse si compte inactif
  - compte temporaire/redemarrage force vers `/password/`
  - droits derives de: `role`, `is_active`, `is_responsable_accredited`, `has_orange_passport`, `can_teach_courses`, rattachements cours
  - middleware global: tout utilisateur connecte avec `password_state != active` est force vers `/password/` (sauf `password-change` et `logout`)

## Dependencies
- Depend de `feature_session_planning_and_calendar` pour les rattachements `CourseEnrollment`.
- Depend de `feature_responsibility_coverage` pour la revocation des affectations futures lors du retrait d'accreditation.
- Depend de `feature_audit_and_operations` pour la tracabilite des actions admin.

## Validation
- `.venv/bin/python -m pytest tests/integration/test_accounts_access.py`
- `.venv/bin/python -m pytest tests/integration/test_admin_permissions.py`
- `.venv/bin/python -m pytest tests/integration/test_admin_responsable_management.py`

## Drift / Limits
- Pas d'inscription autonome membre.
- Le "prof" est une capacite et des affectations, pas un role global stocke.
- Le login reste base sur le nom normalise; les collisions sont gerees a la creation de compte.

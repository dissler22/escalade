# escalade Project Memory

## Role

This file is the transverse map of the repository. It points future work to the
right durable specs, docs, code, and tests before implementation.

This file is not a changelog, task log, or full code dump. Prefer current code
and tests when a detail here becomes stale.

## Product Snapshot

- Product: Django web application for a climbing club to manage free-session
  attendance, reservations, cancellations, account roles, and administration.
- Main flow: authenticated members consult available sessions, reserve or cancel
  places, and view their reservations; authorized admins/responsables manage
  accounts, sessions, reservations, and manual corrections.
- Main surfaces: Django server-rendered pages, admin-oriented views under app
  URL modules, local static CSS, SQLite runtime data, deployment scripts for a
  single VM behind Gunicorn and Nginx.

## How To Read The Repo

- Start here for the global map.
- Read relevant feature specs in `specs/*/`.
- Read operational docs in `docs/` when deployment, runtime settings, backups,
  rollback, or smoke checks are involved.
- Then inspect code and tests in `src/` and `tests/`.

## Active Documentation

- `.specify/memory/constitution.md`: product and delivery governance.
- `specs/001-free-session-booking/`: baseline reservation workflow.
- `specs/002-gcp-vm-deploy/`: single-VM deployment and runtime hardening.
- `specs/003-club-visual-refresh/`: visual refresh and shared CSS/UI patterns.
- `specs/004-session-opener-management/`: opener/responsable management.
- `specs/006-session-calendar/`: session calendar views.
- `specs/007-session-access-types/`: course/session access types.
- `docs/deployment.md`, `docs/operations.md`, `docs/deploy/`: deployment and
  operations notes.
- `docs/rewrite-functional-reference.md`: current functional reference for the
  rewrite.

## Quick Verification

- Main verification command: `.venv/bin/python -m pytest`
- Scope: Django settings, unit services, integration flows, permissions, admin
  session management, booking flows, visual review checks, and OpenAPI contract.

## Repository Topology

- Runtime code: `src/config`, `src/accounts`, `src/sessions`, `src/bookings`,
  `src/audit`.
- UI: `src/templates` and `src/static/css/app.css`.
- Runtime data: local SQLite database in development; production paths are
  configured through environment variables documented in `.env.example` and
  deployment docs.
- Tests: `tests/unit`, `tests/integration`, `tests/contract`, plus Playwright
  assets under `tests/e2e`.
- Deployment: `scripts/deploy`, `docs/deploy`, `docs/deployment.md`.

## Feature Map

### Accounts And Roles

- Code: `src/accounts`.
- Owns authentication helpers, custom user/account fields, admin account
  screens, imports, role and permission-related forms/views.

### Sessions And Calendar

- Code: `src/sessions`.
- Owns courses, session series/occurrences/slots, calendar and detail views,
  admin session management, opener/responsable workflows, and slot coverage
  services.

### Bookings

- Code: `src/bookings`.
- Owns member reservations, cancellations, admin reservation corrections, and
  booking service rules.

### Audit

- Code: `src/audit`.
- Owns trace records and display of history for operationally relevant changes.

### Runtime And Deployment

- Code/docs: `src/config`, `.env.example`, `scripts/deploy`, `docs/`.
- Owns settings loading, local/prod runtime configuration, smoke checks,
  rollback scripts, Gunicorn/Nginx/systemd deployment notes.

## Cross-Feature Invariants

- Permissions are explicit by role; undocumented permissions should be treated
  as denied.
- Booking and manual correction flows that affect session participation should
  leave audit traces.
- UI changes should preserve mobile-first server-rendered flows and shared CSS
  conventions.
- Runtime secrets stay outside the repository and outside admin UI storage.
- SQLite is the current app storage target; schema changes require migrations
  and test coverage.

## Source Of Truth

Use this order when sources disagree:

1. Current code and tests.
2. Relevant `specs/*/` artifacts.
3. This file for cross-repo orientation.
4. Operational docs in `docs/`.
5. Older notes or generated summaries.

## Active Structural Drift

- Specs include historical numbering gaps and one lightweight
  `001-session-access-rights` spec alongside fuller feature specs.
- `docs/features/` is not currently used; durable feature docs live in `specs/`.

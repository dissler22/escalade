# escalade Project Memory

## Role

This file is the transverse map of the repository. It points future work to the
right durable feature docs, ops docs, code, and tests before implementation.

This file is not a changelog, task log, or full code dump. Prefer current code
and tests when a detail here becomes stale.

## Product Snapshot

- Product: Django web application for a climbing club to manage accounts,
  session planning, bookings, slot coverage, and operational administration.
- Main flow: authenticated members consult the weekly calendar, book/cancel
  eligible sessions, and (for accredited users) cover free-practice slots.
- Main surfaces: Django server-rendered pages, admin pages under `/admin/*`,
  local CSS, SQLite runtime data, VM deploy scripts (Gunicorn + Nginx).

## How To Read The Repo

- Start here for the global map.
- Read relevant feature docs in `docs/features/*.md`.
- Read operational docs in `docs/` when deployment, runtime settings, backups,
  rollback, or smoke checks are involved.
- Read `specs/*/` only when deeper historical scope or design rationale is
  needed.
- Then inspect code and tests in `src/` and `tests/`.

## Active Documentation

- `.specify/memory/constitution.md`: product and delivery governance.
- `docs/features/feature_identity_and_access.md`.
- `docs/features/feature_session_planning_and_calendar.md`.
- `docs/features/feature_booking_and_participation.md`.
- `docs/features/feature_responsibility_coverage.md`.
- `docs/features/feature_notifications_and_deadlines.md`.
- `docs/features/feature_audit_and_operations.md`.
- `docs/deployment.md`, `docs/operations.md`, `docs/deploy/`: deployment and
  operations notes.
- `docs/rewrite-functional-reference.md`: functional map of current behavior.
- `specs/*/`: historical specification artifacts and planning detail.

## Quick Verification

- Main verification command: `.venv/bin/python -m pytest`
- Scope: authentication/access, planning/calendar, bookings, coverage,
  notifications, audit traces, runtime settings, and contracts.

## Repository Topology

- Runtime code: `src/config`, `src/accounts`, `src/sessions`, `src/bookings`,
  `src/audit`.
- UI: `src/templates` and `src/static/css/app.css`.
- Runtime data: local SQLite database in development; production paths are
  configured through environment variables documented in `.env.example` and
  deployment docs.
- Tests: `tests/unit`, `tests/integration`, `tests/contract`.
- Deployment: `scripts/deploy`, `docs/deploy`, `docs/deployment.md`.

## Feature Map

### Identity And Access

- Doc: `docs/features/feature_identity_and_access.md`.
- Owns authentication, account lifecycle, access attributes, and account admin.

### Session Planning And Calendar

- Doc: `docs/features/feature_session_planning_and_calendar.md`.
- Owns series/occurrences/slots model and member/admin planning surfaces.

### Booking And Participation

- Doc: `docs/features/feature_booking_and_participation.md`.
- Owns booking/cancellation workflows and admin participation corrections.

### Responsibility Coverage

- Doc: `docs/features/feature_responsibility_coverage.md`.
- Owns responsible assignment lifecycle on free-practice slots.

### Notifications And Deadlines

- Doc: `docs/features/feature_notifications_and_deadlines.md`.
- Owns reminder/auto-cancel deadlines and email automation settings.

### Audit And Operations

- Doc: `docs/features/feature_audit_and_operations.md`.
- Owns audit persistence/history view and VM runtime/deployment operations.

## Cross-Feature Invariants

- Permissions are explicit by role/attributes; undocumented permissions are
  treated as denied.
- Any booking or manual correction affecting participation leaves audit traces.
- Coverage applies only to free-practice slots, never to course occurrences.
- Runtime secrets remain outside the repository and outside admin UI storage.
- SQLite remains the current storage target; schema changes require migrations
  and test coverage.

## Source Of Truth

Use this order when sources disagree:

1. Current code and tests.
2. Relevant `docs/features/*.md`.
3. Relevant `specs/*/` artifacts.
4. This file for cross-repo orientation.
5. Operational docs in `docs/`.
6. Older notes or generated summaries.

## Active Structural Drift

- Specs include historical numbering gaps and one lightweight
  `001-session-access-rights` spec alongside fuller feature specs.
- `docs/features/*.md` and `specs/*/` coexist: feature docs capture current
  durable state, specs keep historical design context and change intent.

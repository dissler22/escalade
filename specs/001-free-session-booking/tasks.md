# Tasks: Reservations de seances libres

**Input**: Design documents from `/specs/001-free-session-booking/`
**Prerequisites**: [plan.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/plan.md), [spec.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/spec.md), [research.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/research.md), [data-model.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/data-model.md), [openapi.yaml](/home/marius/work/repos/escalade/specs/001-free-session-booking/contracts/openapi.yaml)

**Tests**: Tests are included for authentication, booking capacity, admin changes, auditability, and role boundaries because these flows are operationally critical and explicitly constrained by the specification.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently after the foundational phase.

## Format: `[ID] [P?] [Story] Description`

- `[P]` marks tasks that can run in parallel once their dependencies are satisfied.
- `[US1]`, `[US2]`, `[US3]` map tasks to the corresponding user story in the spec.
- Every task includes exact file paths to keep execution unambiguous.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the monolithic web project, local tooling, and baseline documentation.

- [x] T001 Create Python project scaffolding in `/home/marius/work/repos/escalade/pyproject.toml`, `/home/marius/work/repos/escalade/src/manage.py`, `/home/marius/work/repos/escalade/src/config/settings.py`, `/home/marius/work/repos/escalade/src/config/urls.py`, and `/home/marius/work/repos/escalade/src/config/wsgi.py`
- [x] T002 [P] Create application package structure in `/home/marius/work/repos/escalade/src/accounts/__init__.py`, `/home/marius/work/repos/escalade/src/sessions/__init__.py`, `/home/marius/work/repos/escalade/src/bookings/__init__.py`, `/home/marius/work/repos/escalade/src/audit/__init__.py`, and `/home/marius/work/repos/escalade/tests/__init__.py`
- [x] T003 [P] Add local environment and developer defaults in `/home/marius/work/repos/escalade/.env.example`, `/home/marius/work/repos/escalade/.gitignore`, and `/home/marius/work/repos/escalade/README.md`
- [x] T004 [P] Configure test runners in `/home/marius/work/repos/escalade/pytest.ini`, `/home/marius/work/repos/escalade/tests/conftest.py`, and `/home/marius/work/repos/escalade/tests/e2e/playwright.config.ts`
- [x] T005 [P] Document low-cost hosting and deployment assumptions in `/home/marius/work/repos/escalade/docs/deployment.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Put in place the shared data model, role enforcement, audit infrastructure, mobile layout, and admin recovery baseline before user story work starts.

**CRITICAL**: No user story work should begin until this phase is complete.

- [x] T006 Create the custom account model and initial migration in `/home/marius/work/repos/escalade/src/accounts/models.py` and `/home/marius/work/repos/escalade/src/accounts/migrations/0001_initial.py`
- [x] T007 [P] Create session series and session occurrence models with migrations in `/home/marius/work/repos/escalade/src/sessions/models.py` and `/home/marius/work/repos/escalade/src/sessions/migrations/0001_initial.py`
- [x] T008 [P] Create reservation and audit models with migrations in `/home/marius/work/repos/escalade/src/bookings/models.py`, `/home/marius/work/repos/escalade/src/bookings/migrations/0001_initial.py`, `/home/marius/work/repos/escalade/src/audit/models.py`, and `/home/marius/work/repos/escalade/src/audit/migrations/0001_initial.py`
- [x] T009 Implement authentication, role checks, and login/logout routes in `/home/marius/work/repos/escalade/src/accounts/forms.py`, `/home/marius/work/repos/escalade/src/accounts/views.py`, `/home/marius/work/repos/escalade/src/accounts/urls.py`, and `/home/marius/work/repos/escalade/src/config/urls.py`
- [x] T010 [P] Implement shared audit recording helpers in `/home/marius/work/repos/escalade/src/audit/services.py` and `/home/marius/work/repos/escalade/src/audit/apps.py`
- [x] T011 [P] Create the mobile-first base shell in `/home/marius/work/repos/escalade/src/templates/base.html` and `/home/marius/work/repos/escalade/src/static/css/app.css`
- [x] T012 [P] Register admin interfaces and recovery entry points in `/home/marius/work/repos/escalade/src/accounts/admin.py`, `/home/marius/work/repos/escalade/src/sessions/admin.py`, `/home/marius/work/repos/escalade/src/bookings/admin.py`, and `/home/marius/work/repos/escalade/src/audit/admin.py`
- [x] T013 Document account seeding and manual fallback procedures in `/home/marius/work/repos/escalade/docs/operations.md`
- [x] T014 [P] Add foundational auth and audit coverage in `/home/marius/work/repos/escalade/tests/integration/test_accounts_access.py` and `/home/marius/work/repos/escalade/tests/unit/test_audit_service.py`

**Checkpoint**: Foundation ready. Member and admin stories can now proceed with stable models, auth, audit, and recovery primitives.

---

## Phase 3: User Story 1 - Reserver une place depuis son telephone (Priority: P1) MVP

**Goal**: Let an authorized member log in on smartphone, see open future sessions, reserve one place, and cancel their own reservation.

**Independent Test**: On a smartphone viewport, a member can sign in, see open sessions, reserve one available place, see the reservation in their own list, then cancel it and free the place without any admin action.

- [x] T015 [P] [US1] Add member booking flow coverage in `/home/marius/work/repos/escalade/tests/integration/test_member_booking_flow.py`
- [x] T016 [P] [US1] Add duplicate booking and last-seat contention coverage in `/home/marius/work/repos/escalade/tests/unit/test_booking_service.py`
- [x] T017 [P] [US1] Implement member-facing session query helpers in `/home/marius/work/repos/escalade/src/sessions/services.py`
- [x] T018 [US1] Implement booking capacity guards and member cancellation logic in `/home/marius/work/repos/escalade/src/bookings/services.py`
- [x] T019 [US1] Implement member session list, session detail, reservation, and cancellation routes in `/home/marius/work/repos/escalade/src/sessions/views.py`, `/home/marius/work/repos/escalade/src/bookings/views.py`, `/home/marius/work/repos/escalade/src/sessions/urls.py`, `/home/marius/work/repos/escalade/src/bookings/urls.py`, and `/home/marius/work/repos/escalade/src/config/urls.py`
- [x] T020 [P] [US1] Create smartphone-first member templates in `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`, `/home/marius/work/repos/escalade/src/templates/sessions/session_detail.html`, and `/home/marius/work/repos/escalade/src/templates/bookings/my_reservations.html`
- [x] T021 [US1] Emit reservation and cancellation audit events with user feedback in `/home/marius/work/repos/escalade/src/bookings/services.py` and `/home/marius/work/repos/escalade/src/audit/services.py`
- [x] T022 [US1] Record smartphone MVP validation notes in `/home/marius/work/repos/escalade/specs/001-free-session-booking/quickstart.md`

**Checkpoint**: User Story 1 is independently functional when a seeded member can complete the entire booking and cancellation flow on mobile.

---

## Phase 4: User Story 2 - Ouvrir et parametrer les seances (Priority: P2)

**Goal**: Let an administrator create one-off sessions and weekly series, override one week without changing others, and manually open, close, or cancel sessions.

**Independent Test**: An admin can create a weekly series, create a single-session override for one week, adjust capacity, and manually change open or closed state without affecting unrelated weeks.

- [x] T023 [P] [US2] Add admin session management coverage in `/home/marius/work/repos/escalade/tests/integration/test_admin_session_management.py`
- [x] T024 [P] [US2] Add weekly override regression coverage in `/home/marius/work/repos/escalade/tests/unit/test_session_occurrence_overrides.py`
- [x] T025 [US2] Implement session series generation and override logic in `/home/marius/work/repos/escalade/src/sessions/services.py`
- [x] T026 [US2] Implement admin forms and views for series and occurrence management in `/home/marius/work/repos/escalade/src/sessions/forms.py`, `/home/marius/work/repos/escalade/src/sessions/views_admin.py`, and `/home/marius/work/repos/escalade/src/sessions/urls_admin.py`
- [x] T027 [P] [US2] Create admin templates for series, occurrence editing, and weekly overrides in `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_list.html`, `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_form.html`, and `/home/marius/work/repos/escalade/src/templates/admin/sessions/occurrence_form.html`
- [x] T028 [US2] Implement open, close, and cancel transitions with audit emission in `/home/marius/work/repos/escalade/src/sessions/services.py` and `/home/marius/work/repos/escalade/src/audit/services.py`
- [x] T029 [US2] Expose admin session management navigation and routes in `/home/marius/work/repos/escalade/src/config/urls.py` and `/home/marius/work/repos/escalade/src/templates/base.html`

**Checkpoint**: User Story 2 is independently functional when an admin can manage a weekly schedule and a one-week exception without breaking the member booking flow.

---

## Phase 5: User Story 3 - Corriger manuellement un cas operationnel (Priority: P3)

**Goal**: Let an administrator inspect reservations, manually add or remove a reservation, disable an account, and read the audit history for a session.

**Independent Test**: An admin can open a future session, see the attendee list, add or remove a reservation manually, deactivate a member account, and inspect a complete audit trail explaining what changed.

- [x] T030 [P] [US3] Add admin correction and audit-history coverage in `/home/marius/work/repos/escalade/tests/integration/test_admin_booking_corrections.py`
- [x] T031 [P] [US3] Add admin-only permissions coverage for correction and account status changes in `/home/marius/work/repos/escalade/tests/integration/test_admin_permissions.py`
- [x] T032 [US3] Implement admin reservation correction methods in `/home/marius/work/repos/escalade/src/bookings/services.py`
- [x] T033 [US3] Implement admin correction and account-status routes in `/home/marius/work/repos/escalade/src/bookings/views_admin.py`, `/home/marius/work/repos/escalade/src/accounts/views_admin.py`, `/home/marius/work/repos/escalade/src/bookings/urls_admin.py`, and `/home/marius/work/repos/escalade/src/accounts/urls_admin.py`
- [x] T034 [P] [US3] Create admin templates for reservation corrections, audit history, and account status in `/home/marius/work/repos/escalade/src/templates/admin/bookings/session_reservations.html`, `/home/marius/work/repos/escalade/src/templates/admin/audit/session_history.html`, and `/home/marius/work/repos/escalade/src/templates/admin/accounts/account_list.html`
- [x] T035 [US3] Implement session audit history queries and rendering in `/home/marius/work/repos/escalade/src/audit/views.py`, `/home/marius/work/repos/escalade/src/audit/urls.py`, and `/home/marius/work/repos/escalade/src/audit/services.py`
- [x] T036 [US3] Extend the manual recovery guide for disputed or failed reservations in `/home/marius/work/repos/escalade/docs/operations.md` and `/home/marius/work/repos/escalade/specs/001-free-session-booking/quickstart.md`

**Checkpoint**: User Story 3 is independently functional when admin correction and audit lookup can resolve an operational incident without database-level intervention.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish cross-story verification, contract alignment, and operational review.

- [x] T037 [P] Add contract-level API coverage in `/home/marius/work/repos/escalade/tests/contract/test_openapi_contract.py`
- [x] T038 Review data minimization and access scope against the spec in `/home/marius/work/repos/escalade/src/accounts/models.py`, `/home/marius/work/repos/escalade/src/audit/models.py`, and `/home/marius/work/repos/escalade/docs/operations.md`
- [x] T039 [P] Run the MVP smoke checklist and record outcomes in `/home/marius/work/repos/escalade/specs/001-free-session-booking/quickstart.md`
- [x] T040 Confirm final low-cost deployment and rollback notes in `/home/marius/work/repos/escalade/docs/deployment.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 can start immediately.
- Phase 2 depends on Phase 1 and blocks all user stories.
- Phase 3 depends on Phase 2 and defines the MVP.
- Phase 4 depends on Phase 2 and should follow Phase 3 for the first demo because admins need a live member flow to validate end-to-end behavior.
- Phase 5 depends on Phase 2 and should follow Phase 3 because it builds on booking behavior and audit traces already exercised by members.
- Phase 6 depends on whichever user stories are included in the release target.

### User Story Dependencies

- US1 is the first delivery target and the recommended MVP scope.
- US2 can begin after the foundational phase, but it is safest to merge after US1 because it changes the same session domain and should not destabilize the booking flow.
- US3 can begin after the foundational phase, but it should merge after US1 because it depends on realistic reservation and audit states.

### Suggested Completion Order

1. Phase 1 Setup
2. Phase 2 Foundational
3. Phase 3 US1 MVP
4. Phase 4 US2
5. Phase 5 US3
6. Phase 6 Polish

## Parallel Opportunities

- In Phase 1, T002, T003, T004, and T005 can run in parallel after T001 starts the project structure.
- In Phase 2, T007, T008, T010, T011, T012, and T014 can run in parallel once T006 has established the base account model.
- In US1, T015 and T016 can run in parallel; T017 and T020 can also run in parallel before wiring the final views in T019.
- In US2, T023 and T024 can run in parallel; T027 can proceed in parallel with T025 once form fields are known.
- In US3, T030 and T031 can run in parallel; T034 can proceed in parallel with T032 once the correction screens are scoped.
- In Phase 6, T037 and T039 can run in parallel while T038 and T040 close documentation gaps.

## Parallel Example: User Story 1

```bash
Task: "T015 [US1] Add member booking flow coverage in tests/integration/test_member_booking_flow.py"
Task: "T016 [US1] Add duplicate booking and last-seat contention coverage in tests/unit/test_booking_service.py"

Task: "T017 [US1] Implement member-facing session query helpers in src/sessions/services.py"
Task: "T020 [US1] Create smartphone-first member templates in src/templates/sessions/session_list.html, src/templates/sessions/session_detail.html, and src/templates/bookings/my_reservations.html"
```

## Parallel Example: User Story 2

```bash
Task: "T023 [US2] Add admin session management coverage in tests/integration/test_admin_session_management.py"
Task: "T024 [US2] Add weekly override regression coverage in tests/unit/test_session_occurrence_overrides.py"

Task: "T025 [US2] Implement session series generation and override logic in src/sessions/services.py"
Task: "T027 [US2] Create admin templates for series, occurrence editing, and weekly overrides in src/templates/admin/sessions/"
```

## Parallel Example: User Story 3

```bash
Task: "T030 [US3] Add admin correction and audit-history coverage in tests/integration/test_admin_booking_corrections.py"
Task: "T031 [US3] Add admin-only permissions coverage in tests/integration/test_admin_permissions.py"

Task: "T032 [US3] Implement admin reservation correction methods in src/bookings/services.py"
Task: "T034 [US3] Create admin templates for reservation corrections, audit history, and account status in src/templates/admin/"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 only.
3. Validate the smartphone member journey, audit events, and manual fallback notes.
4. Demo or ship the MVP before adding broader admin convenience features.

### Incremental Delivery

1. Deliver US1 to prove booking, cancellation, capacity control, and mobile usability.
2. Deliver US2 to let admins manage the weekly calendar in-app instead of by seed data only.
3. Deliver US3 to close the operational recovery loop with manual corrections and account control.
4. Finish with Phase 6 cross-cutting review and contract alignment.

### Parallel Team Strategy

1. One developer completes setup while another drafts docs and test harness files.
2. The team converges on the foundational phase before branching into stories.
3. After the foundation is stable, one developer can take US1 while another prepares US2 screens or US3 templates, but US1 remains the merge priority.

## Notes

- `product.md` and `test-registry.md` were not present in `/home/marius/work/repos/escalade/.specify/memory/`, so task generation relied on the current feature spec, plan, research, and constitution only.
- All tasks use the required checklist format with checkbox, task ID, optional `[P]`, required `[USn]` labels for story phases, and exact file paths.

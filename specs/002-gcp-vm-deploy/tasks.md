# Tasks: Deploiement VM simple

**Input**: Design documents from `/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/`
**Prerequisites**: [plan.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/plan.md), [spec.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/spec.md), [research.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/research.md), [data-model.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/data-model.md), [openapi.yaml](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/contracts/openapi.yaml), [quickstart.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/quickstart.md)

**Tests**: Tests are included for runtime settings and the critical public journey because this feature changes production safety, public exposure, and rollback-sensitive behavior.

**Organization**: Tasks are grouped by user story so the public access path, initial VM provisioning, and release rollback flow can be implemented and validated incrementally.

## Format: `[ID] [P?] [Story] Description`

- `[P]` marks tasks that can run in parallel once their dependencies are satisfied.
- `[US1]`, `[US2]`, `[US3]` map tasks to the corresponding user story in the spec.
- Every task includes exact file paths to keep execution unambiguous.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the repo for production deployment artifacts, runtime dependencies, and operator-facing entry points.

- [X] T001 Add the production runtime dependency and operator command references in `/home/marius/work/repos/escalade/pyproject.toml` and `/home/marius/work/repos/escalade/README.md`
- [X] T002 [P] Expand the production environment sample for secrets, hosts, shared paths, and logging in `/home/marius/work/repos/escalade/.env.example`
- [X] T003 [P] Create the deployment artifact index and file ownership conventions in `/home/marius/work/repos/escalade/docs/deploy/README.md`
- [X] T004 [P] Create the deployment script inventory and usage notes in `/home/marius/work/repos/escalade/scripts/deploy/README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Put in place the shared runtime configuration, release layout helpers, contract checks, and manual recovery baseline before any user story work starts.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T005 Create the environment parsing helper for production-safe settings in `/home/marius/work/repos/escalade/src/config/env.py`
- [X] T006 Implement externalized Django settings, persistent SQLite/static paths, and proxy-aware defaults in `/home/marius/work/repos/escalade/src/config/settings.py`
- [X] T007 [P] Add runtime settings coverage for secrets, debug mode, allowed hosts, and shared paths in `/home/marius/work/repos/escalade/tests/unit/test_settings_runtime.py`
- [X] T008 [P] Extend the public route contract coverage for production smoke URLs in `/home/marius/work/repos/escalade/tests/contract/test_openapi_contract.py`
- [X] T009 [P] Create shared release-layout and path helper functions in `/home/marius/work/repos/escalade/scripts/deploy/common.sh`
- [X] T010 Document shared-state directories, operator roles, and manual recovery baseline in `/home/marius/work/repos/escalade/docs/deployment.md` and `/home/marius/work/repos/escalade/docs/operations.md`

**Checkpoint**: Foundation ready. Story work can now proceed with stable runtime configuration, a known release layout, and a documented manual fallback path.

---

## Phase 3: User Story 1 - Ouvrir l'application depuis le telephone apres mise en ligne (Priority: P1) MVP

**Goal**: Let a member reach the public URL on smartphone, authenticate, load the session pages, and receive styles and redirects correctly after deployment.

**Independent Test**: With production-style settings and the published front-door templates in place, a tester can open the public URL, reach `/login/`, authenticate, load `/sessions/`, open `/bookings/mine/`, and confirm that `/static/css/app.css` is served.

- [X] T011 [P] [US1] Add regression coverage for login, session list, and member reservations under production-style settings in `/home/marius/work/repos/escalade/tests/integration/test_accounts_access.py` and `/home/marius/work/repos/escalade/tests/integration/test_member_booking_flow.py`
- [X] T012 [P] [US1] Create the public smoke-check script for `/`, `/login/`, `/sessions/`, `/bookings/mine/`, and `/static/css/app.css` in `/home/marius/work/repos/escalade/scripts/deploy/smoke_check.sh`
- [X] T013 [US1] Add trusted-host, CSRF/proxy, static collection, and secure redirect settings in `/home/marius/work/repos/escalade/src/config/settings.py`
- [X] T014 [P] [US1] Create the Nginx and Gunicorn service templates for the public entry point in `/home/marius/work/repos/escalade/docs/deploy/nginx/escalade.conf` and `/home/marius/work/repos/escalade/docs/deploy/systemd/escalade.service`
- [X] T015 [US1] Capture the smartphone/public validation steps and expected smoke outcomes in `/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/quickstart.md`

**Checkpoint**: User Story 1 is independently functional when the public entry stack can serve the existing mobile journey without exposing Django directly.

---

## Phase 4: User Story 2 - Mettre en ligne la premiere version sur une VM unique (Priority: P2)

**Goal**: Let a maintainer provision a clean VM, install the app on the shared layout, enable automatic restart, and complete the first deployment from documentation and scripts.

**Independent Test**: Starting from a clean VM of the same class, a maintainer can run the provisioning and first-release steps, reboot the machine, and confirm that the service comes back without editing source files.

- [X] T016 [P] [US2] Create the VM provisioning script for Python, Nginx, the app user, and shared directories in `/home/marius/work/repos/escalade/scripts/deploy/provision_vm.sh`
- [X] T017 [P] [US2] Create the first-release install script that builds the virtualenv, installs runtime dependencies, runs migrations, and collects static files in `/home/marius/work/repos/escalade/scripts/deploy/first_release.sh`
- [X] T018 [US2] Document the initial deployment checklist, exposed ports, file permissions, and reboot verification in `/home/marius/work/repos/escalade/docs/deployment.md`
- [X] T019 [US2] Record the clean-VM installation procedure and expected post-reboot checks in `/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/quickstart.md`

**Checkpoint**: User Story 2 is independently functional when a clean VM can be brought to a repeatable first production release with the repo artifacts alone.

---

## Phase 5: User Story 3 - Publier une mise a jour avec repli rapide (Priority: P3)

**Goal**: Let a maintainer take a backup, publish a new release, verify the critical journey, and roll back quickly if verification or migrations fail.

**Independent Test**: A maintainer can create a pre-release backup, activate a new release, fail verification intentionally, restore the previous release, and recover a coherent SQLite state within the documented rollback window.

- [X] T020 [P] [US3] Create the SQLite backup and restore helpers for pre-release snapshots in `/home/marius/work/repos/escalade/scripts/deploy/backup_sqlite.sh` and `/home/marius/work/repos/escalade/scripts/deploy/restore_sqlite.sh`
- [X] T021 [P] [US3] Create the release switching and rollback scripts around `releases/current/shared` in `/home/marius/work/repos/escalade/scripts/deploy/release.sh` and `/home/marius/work/repos/escalade/scripts/deploy/rollback.sh`
- [X] T022 [US3] Add operator logging, maintenance-window steps, and rollback journal requirements in `/home/marius/work/repos/escalade/docs/operations.md` and `/home/marius/work/repos/escalade/docs/deployment.md`
- [X] T023 [US3] Extend the runbook with standard release, failed verification, failed migration, and rollback drill scenarios in `/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/quickstart.md`

**Checkpoint**: User Story 3 is independently functional when the operator can recover the previous release and coherent data without ad hoc shell work.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize verification assets, review secret handling, and record end-to-end recovery results.

- [X] T024 [P] Update the production entry contract and final verification notes in `/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/contracts/openapi.yaml`
- [X] T025 Review secret handling, data minimization, and trace retention in `/home/marius/work/repos/escalade/.env.example`, `/home/marius/work/repos/escalade/src/config/settings.py`, and `/home/marius/work/repos/escalade/docs/operations.md`
- [ ] T026 [P] Validate the end-to-end smoke, reboot, and rollback checklists and record outcomes in `/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/quickstart.md`
- [X] T027 Confirm the final VM-specific rollout and rollback notes for `34.71.54.146` in `/home/marius/work/repos/escalade/docs/deployment.md` and `/home/marius/work/repos/escalade/README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 can start immediately.
- Phase 2 depends on Phase 1 and blocks all user stories.
- Phase 3 depends on Phase 2 and defines the minimum public-access MVP.
- Phase 4 depends on Phase 2 and should follow Phase 3 because it packages and executes the public-access artifacts on a clean VM.
- Phase 5 depends on Phase 4 because rollback depends on the release layout, first-release script, and shared-state conventions already being in place.
- Phase 6 depends on the user stories included in the release target.

### User Story Dependencies

- **US1 (P1)** starts first because it defines the public-access outcome that the deployment must preserve.
- **US2 (P2)** depends on the foundational phase and reuses the US1 runtime and front-door artifacts to make the first VM deployment repeatable.
- **US3 (P3)** depends on US2 because safe rollback presumes an existing release layout, provisioning flow, and first-release process.

### Suggested Completion Order

1. Phase 1 Setup
2. Phase 2 Foundational
3. Phase 3 US1 MVP
4. Phase 4 US2
5. Phase 5 US3
6. Phase 6 Polish

## Parallel Opportunities

- In Phase 1, T002, T003, and T004 can run in parallel after T001 establishes the runtime scope.
- In Phase 2, T007, T008, and T009 can run in parallel once T005 and T006 define the runtime contract.
- In US1, T011, T012, and T014 can run in parallel while T013 finalizes the Django production behavior.
- In US2, T016 and T017 can run in parallel once the shared layout in `scripts/deploy/common.sh` is stable.
- In US3, T020 and T021 can run in parallel before T022 and T023 finalize the operator runbook.
- In Phase 6, T024 and T026 can run in parallel while T025 and T027 close the remaining documentation checks.

## Parallel Example: User Story 1

```bash
Task: "T011 [US1] Add regression coverage for login, session list, and member reservations under production-style settings in tests/integration/test_accounts_access.py and tests/integration/test_member_booking_flow.py"
Task: "T012 [US1] Create the public smoke-check script for /, /login/, /sessions/, /bookings/mine/, and /static/css/app.css in scripts/deploy/smoke_check.sh"
Task: "T014 [US1] Create the Nginx and Gunicorn service templates for the public entry point in docs/deploy/nginx/escalade.conf and docs/deploy/systemd/escalade.service"
```

## Parallel Example: User Story 2

```bash
Task: "T016 [US2] Create the VM provisioning script for Python, Nginx, the app user, and shared directories in scripts/deploy/provision_vm.sh"
Task: "T017 [US2] Create the first-release install script that builds the virtualenv, installs runtime dependencies, runs migrations, and collects static files in scripts/deploy/first_release.sh"
```

## Parallel Example: User Story 3

```bash
Task: "T020 [US3] Create the SQLite backup and restore helpers for pre-release snapshots in scripts/deploy/backup_sqlite.sh and scripts/deploy/restore_sqlite.sh"
Task: "T021 [US3] Create the release switching and rollback scripts around releases/current/shared in scripts/deploy/release.sh and scripts/deploy/rollback.sh"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 to lock down the public entry, static serving, and smoke validation.
3. Validate the smartphone public journey and contract coverage.
4. Proceed to clean-VM provisioning only after the public-access baseline is stable.

### Incremental Delivery

1. Deliver US1 to make the deployed app safe and reachable from the public front door.
2. Deliver US2 to make first deployment on the target VM repeatable without source edits.
3. Deliver US3 to close the backup, release, verification, and rollback loop.
4. Finish with Phase 6 cross-cutting review and recorded recovery drills.

### Parallel Team Strategy

1. One developer can handle runtime settings while another prepares deployment docs and script inventories during Phases 1 and 2.
2. After the foundation is stable, one developer can take the public-access tasks in US1 while another prepares the provisioning scripts for US2.
3. Rollback automation in US3 should merge only after the first-release path from US2 is already coherent.

## Notes

- `.specify/memory/product.md` and `.specify/memory/test-registry.md` were not present in `/home/marius/work/repos/escalade/.specify/memory/`, so task generation relied on the current feature spec, plan, research, data model, contract, quickstart, constitution, and the existing feature spec in `/home/marius/work/repos/escalade/specs/001-free-session-booking/spec.md`.
- All tasks use the required checklist format with checkbox, task ID, optional `[P]`, required `[USn]` labels for story phases, and exact file paths.

---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Include tests when requested by the specification, when the change is risky, or when they are the clearest way to verify roles, auditability, or recovery behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Prioritize the MVP story before advanced automation work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions
- Include explicit tasks for audit trail, role enforcement, smartphone validation and manual recovery whenever the feature touches them

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize project dependencies and local tooling
- [ ] T003 [P] Document zero or near-zero cost assumptions for the selected stack
- [ ] T004 [P] Define the primary smartphone viewport and validation approach for the feature

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T005 Setup base data model and migrations framework
- [ ] T006 [P] Implement authentication and role enforcement foundations
- [ ] T007 [P] Establish audit event recording for registration, cancellation and admin correction flows
- [ ] T008 [P] Set up admin-visible error handling and recovery hooks
- [ ] T009 Configure environment and secrets management consistent with minimal data handling
- [ ] T010 Document the manual fallback path for core operational failures

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own, starting on smartphone]

### Tests for User Story 1 (include when needed)

- [ ] T011 [P] [US1] Add verification for the primary journey in tests/[type]/[name]
- [ ] T012 [P] [US1] Add verification for role enforcement or validation edge cases in tests/[type]/[name]

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create or update the required entity models in [file paths]
- [ ] T014 [US1] Implement the core service or action in [file path]
- [ ] T015 [US1] Implement the smartphone-first UI or endpoint in [file path]
- [ ] T016 [US1] Add audit trail emission for the story's registration or cancellation events
- [ ] T017 [US1] Add admin-visible handling or manual correction support for failure cases
- [ ] T018 [US1] Validate the story on the primary smartphone viewport and record any constraints

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (include when needed)

- [ ] T019 [P] [US2] Add verification for the story in tests/[type]/[name]
- [ ] T020 [P] [US2] Add verification for newly introduced audit or recovery behavior in tests/[type]/[name]

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create or update required models in [file paths]
- [ ] T022 [US2] Implement the story service, UI or endpoint in [file paths]
- [ ] T023 [US2] Extend auditability, role enforcement and admin handling as required
- [ ] T024 [US2] Document any new manual operation introduced by the story

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (include when needed)

- [ ] T025 [P] [US3] Add verification for the story in tests/[type]/[name]
- [ ] T026 [P] [US3] Add verification for permissions, auditability or recovery edge cases in tests/[type]/[name]

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create or update required models in [file paths]
- [ ] T028 [US3] Implement the story service, UI or endpoint in [file paths]
- [ ] T029 [US3] Extend auditability, role enforcement and manual recovery support as required

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Update operational documentation in docs/ or specs/
- [ ] TXXX Review data minimization and access scope against the approved spec
- [ ] TXXX [P] Add additional regression coverage where needed
- [ ] TXXX Validate the manual recovery path end-to-end
- [ ] TXXX Confirm advanced automation tasks still come after the manual MVP baseline

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel if capacity allows
  - Or sequentially in priority order (P1 -> P2 -> P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts first because it defines the MVP and the manual baseline
- **User Story 2 (P2)**: Can start after Foundational; must not break US1 independence
- **User Story 3 (P3)**: Can start after Foundational; must not introduce automation that bypasses traceability or manual recovery

### Within Each User Story

- Add verification first when the spec or risk level requires it
- Models before services
- Services before UI or endpoints
- Core implementation before integration
- Auditability, role enforcement and manual recovery before story sign-off
- Story complete before moving advanced automation ahead of priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel within Phase 2
- Once Foundational phase completes, user stories can proceed in parallel if staffing allows
- Tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members, provided MVP priority is respected

---

## Parallel Example: User Story 1

```bash
# Launch verification relevant to the MVP story together:
Task: "Add verification for the primary journey in tests/[type]/[name]"
Task: "Add verification for role enforcement or validation edge cases in tests/[type]/[name]"

# Launch implementation work on different files together:
Task: "Create or update the required entity models in [file paths]"
Task: "Implement the smartphone-first UI or endpoint in [file path]"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate audit trail, role enforcement, smartphone flow and manual recovery
5. Deploy or demo if ready

### Incremental Delivery

1. Complete Setup and Foundational -> foundation ready
2. Add User Story 1 -> test independently -> deploy or demo MVP
3. Add User Story 2 -> test independently -> deploy or demo
4. Add User Story 3 -> test independently -> deploy or demo
5. Keep advanced automation behind a proven manual baseline

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup and Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Integrate only after each story preserves traceability and role boundaries

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to a specific user story for traceability
- Each user story should be independently completable and testable
- Prefer the simplest operationally sustainable implementation first
- Do not hide unresolved business rules in code; keep them in the spec
- Avoid vague tasks, same-file conflicts and automation that ships before the manual baseline

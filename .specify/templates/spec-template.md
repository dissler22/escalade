# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language, with the smartphone flow first]

**Why this priority**: [Explain the value and why this is the MVP slice]

**Independent Test**: [Describe how this can be tested independently on the web app and what value it delivers]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it comes after P1]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it is lower priority]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: Replace the content in this section with feature-specific
  edge cases, especially those affecting registrations, cancellations,
  conflicting permissions or degraded manual operation.
-->

- What happens when a participant tries to register after remaining capacity reaches zero?
- How does the system behave when an admin must correct a failed registration or cancellation manually?
- What happens when a role attempts an action not explicitly allowed by the spec?
- How is the flow handled when connectivity is poor on a smartphone browser?

## Requirements *(mandatory)*

### Roles & Rules

- **Actor Roles**: [List each role involved in the feature and the actions it may perform]
- **Explicit Permissions**: [State what each role can view, create, modify, cancel or administer]
- **Resolved Business Rules**: [List the rules decided by this feature]
- **Open Business Rules**: [List unresolved rules as NEEDS CLARIFICATION items instead of inventing behavior]

### Functional Requirements

- **FR-001**: System MUST [specific capability aligned with the P1 smartphone flow]
- **FR-002**: System MUST [specific capability for the responsible role or admin]
- **FR-003**: System MUST record [audit event] when [registration or cancellation action occurs]
- **FR-004**: System MUST provide [manual fallback or correction path] for admins when the nominal flow fails
- **FR-005**: System MUST enforce [permission or validation rule]

*Example of marking unclear requirements:*

- **FR-006**: System MUST apply [NEEDS CLARIFICATION: reservation priority rule not yet decided]
- **FR-007**: System MUST retain personal data for [NEEDS CLARIFICATION: retention duration not yet decided]

### Audit & Operations

- **Audit Events**: [List each registration/cancellation/admin correction event that must be traceable]
- **Operational Procedure**: [Describe the normal admin handling path in plain language]
- **Manual Recovery**: [Describe how an authorized admin restores a correct state if automation fails]
- **Cost Impact**: [State any recurring cost introduced; default expectation is zero or near-zero]

### Data & Privacy

- **Collected Data**: [List each data item created, viewed or updated by the feature]
- **Purpose of Each Data Item**: [Explain why each item is needed for operations]
- **Access Scope**: [Which roles can access which data]
- **Retention / Deletion Approach**: [How data is retained, anonymized or deleted]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic, measurable and aligned with smartphone use,
  operational simplicity and traceability.
-->

### Measurable Outcomes

- **SC-001**: [Primary smartphone user can complete the core flow within a defined time]
- **SC-002**: [Authorized admin can verify or correct a registration state within a defined time]
- **SC-003**: [All specified registration/cancellation events are traceable in the audit history]
- **SC-004**: [Feature runs within the approved zero or near-zero recurring cost envelope]

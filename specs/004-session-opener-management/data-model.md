# Data Model: Gestion des responsables de pratique libre

## Overview

La conception technique ajoute un niveau `creneau reservable` sous la seance datee afin de respecter la spec 004 tout en conservant les regles de reservation de la spec 001.

## Entities

### User

- **Purpose**: represente une personne pouvant se connecter a l application.
- **Existing fields reused**:
  - `id`
  - `full_name`
  - `email`
  - `role` with values `member|admin`
  - `is_active`
  - `password_state`
- **New fields**:
  - `is_responsable_accredited` boolean, default `false`
  - `responsable_accredited_at` datetime nullable
  - `responsable_accredited_by_id` nullable foreign key to `User`
- **Validation rules**:
  - un utilisateur inactif ne peut ni reserver ni couvrir un creneau
  - un utilisateur non accredite responsable ne peut pas devenir responsable d un creneau
  - un admin peut etre accredite ou agir comme responsable sans changer son role principal

### SessionSeries

- **Purpose**: conserve la regle hebdomadaire existante de creation de seances.
- **Existing fields reused**:
  - `label`
  - `weekday`
  - `start_time`
  - `end_time`
  - `default_capacity`
  - `is_active`
  - `created_by`
- **Likely additions**:
  - aucune obligatoire pour le MVP si le decoupage en creneaux est derive des horaires existants
- **Validation rules**:
  - `end_time > start_time`
  - `default_capacity >= 1`

### SessionOccurrence

- **Purpose**: devient la seance parent datee visible aux adherents et a l admin.
- **Existing fields reused**:
  - `id`
  - `series`
  - `label`
  - `session_date`
  - `start_time`
  - `end_time`
  - `status`
  - `notes`
  - `created_by`
  - `created_at`
  - `updated_at`
- **Field changes**:
  - `capacity` n est plus la source de reservation directe; elle devient soit retiree, soit derivee des creneaux selon la strategie de migration retenue
  - `remaining_capacity` devient derive de l aggregation des creneaux actifs
- **Validation rules**:
  - une seance parent doit couvrir une plage horaire continue
  - une seance parent doit posseder au moins un creneau enfant
  - les creneaux enfants doivent couvrir toute la duree de la seance sans chevauchement

### SessionSlot

- **Purpose**: represente le creneau reservable et responsabilisable de 90 minutes maximum.
- **Fields**:
  - `id`
  - `occurrence_id` foreign key to `SessionOccurrence`
  - `start_time`
  - `end_time`
  - `capacity`
  - `status` with values `draft|open|closed|cancelled|completed`
  - `coverage_status` derived `uncovered|covered|cancelled`
  - `sequence_index` positive integer for ordering within parent session
  - `created_at`
  - `updated_at`
- **Validation rules**:
  - `end_time > start_time`
  - duration `<= 90 minutes`
  - `capacity >= 1`
  - uniqueness on `(occurrence_id, sequence_index)`
  - no overlap between slots of the same parent occurrence
- **State transitions**:
  - `draft -> open|cancelled`
  - `open -> closed|cancelled|completed`
  - `closed -> open|cancelled|completed`
  - `cancelled` terminal
  - `completed` terminal

### Reservation

- **Purpose**: represente l inscription pratiquant sur un creneau.
- **Field changes**:
  - replace `occurrence_id` by `slot_id` foreign key to `SessionSlot`
  - keep `user_id`
  - keep `status` with `active|cancelled`
  - keep `created_by_role`
  - keep `cancellation_reason`
  - keep timestamps
- **Validation rules**:
  - unique active reservation per `(slot_id, user_id)`
  - forbidden if slot status is not reservable
  - forbidden if slot has started
  - forbidden if slot remaining capacity is zero
- **State transitions**:
  - `active -> cancelled`

### ResponsibleAssignment

- **Purpose**: represente la prise de responsabilite d un creneau par un utilisateur accredite.
- **Fields**:
  - `id`
  - `slot_id` foreign key to `SessionSlot`
  - `user_id` foreign key to `User`
  - `status` with values `active|released|revoked`
  - `assigned_by_user_id` nullable foreign key to `User`
  - `release_reason` text or short code nullable
  - `assigned_at`
  - `released_at` nullable
- **Validation rules**:
  - a slot may have at most one active assignment
  - a user must be active and responsable-accredited at assignment time, unless explicit admin override is supported for admins
  - assignment forbidden if slot is cancelled or already started
- **State transitions**:
  - `active -> released|revoked`

### AuditEntry

- **Purpose**: conserve un historique unique des actions metier et systeme.
- **Existing fields reused**:
  - `actor_user`
  - `actor_role_snapshot`
  - `action_type`
  - `target_type`
  - `target_id`
  - `reason`
  - `metadata_snapshot`
  - `created_at`
- **Likely additions**:
  - `slot_id` nullable foreign key to `SessionSlot`
  - keep `occurrence_id` for parent session context
  - keep `reservation_id` where relevant
  - optional `responsible_assignment_id` nullable
- **Action types to add**:
  - `responsable_accreditation_granted`
  - `responsable_accreditation_revoked`
  - `slot_created`
  - `slot_updated`
  - `slot_cancelled`
  - `responsable_assignment_taken`
  - `responsable_assignment_released`
  - `responsable_assignment_revoked`
  - `slot_reminder_sent`
  - `slot_auto_cancelled_uncovered`
  - `slot_cancellation_notice_sent`

### NotificationSetting

- **Purpose**: expose l adresse d envoi active sans stocker le secret SMTP en base.
- **Implementation-facing shape**:
  - derive from application settings rather than a persisted table for MVP
- **Exposed fields**:
  - `sender_email`
  - `sender_display_name`
  - `notifications_enabled`
- **Validation rules**:
  - sender email must be syntactically valid
  - secret is environment-only and never surfaced in admin UI
  - seuls les administrateurs voient l adresse d envoi active

## Relationships

- `SessionSeries 1 -> n SessionOccurrence`
- `SessionOccurrence 1 -> n SessionSlot`
- `SessionSlot 1 -> n Reservation`
- `SessionSlot 1 -> n ResponsibleAssignment`
- `SessionSlot 1 -> 0..1 active ResponsibleAssignment`
- `User 1 -> n Reservation`
- `User 1 -> n ResponsibleAssignment`
- `SessionOccurrence 1 -> n AuditEntry`
- `SessionSlot 1 -> n AuditEntry`

## Derived Values

- `SessionSlot.remaining_capacity = capacity - active_reservations_count`
- `SessionSlot.current_responsable = active ResponsibleAssignment.user`
- `SessionSlot.coverage_status`:
  - `cancelled` if slot status is `cancelled`
  - `covered` if one active assignment exists
  - `uncovered` otherwise
- `SessionOccurrence.coverage_summary`:
  - count of `covered`, `uncovered`, `cancelled` child slots

## Migration Notes

- Existing `SessionOccurrence` rows become parent sessions.
- Each existing occurrence must receive one initial child slot covering its current start/end time and current capacity.
- Existing `Reservation` rows must be reassigned from parent occurrence to the generated child slot.
- Existing audit rows tied to occurrence-only actions remain valid; future audit entries should also target the child slot where applicable.

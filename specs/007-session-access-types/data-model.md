# Data Model: Types de seance et droits d acces

## Overview

La feature 007 ajoute deux dimensions persistantes au produit: le type de seance et les droits d inscription associes a chaque utilisateur. Le design conserve la structure existante de series, occurrences, reservations et audit, puis ajoute des relations explicites pour le passport orange, les cours et l affectation prof.

## Entities

### User

- **Purpose**: represente une personne connectable pouvant etre adherent, referent/responsable, prof ou admin selon plusieurs dimensions cumulables.
- **Existing fields reused**:
  - `id`
  - `full_name`
  - `email`
  - `role` with values `member|admin`
  - `is_responsable_accredited`
  - `responsable_accredited_at`
  - `responsable_accredited_by_id`
  - `is_active`
  - `password_state`
- **New fields**:
  - `has_orange_passport` boolean, default `false`
  - `orange_passport_granted_at` datetime nullable
  - `orange_passport_granted_by_id` nullable foreign key to `User`
- **Derived permissions**:
  - `can_book_free_practice` when user is active and has orange passport or responsable accreditation, with admin override retained
  - `can_cover_slots` remains tied to admin override or responsable accreditation
  - `can_edit_course_occurrence(occurrence)` when the user is active and owns the teacher assignment of a course occurrence
- **Validation rules**:
  - un utilisateur inactif ne peut ni s inscrire ni editer une occurrence
  - le passport orange n accorde aucun droit d edition
  - l accreditation referent n accorde aucun droit d edition sur les cours

### SessionSeries

- **Purpose**: represente un modele recurrent de seances qui peut desormais decrire soit une pratique libre soit un cours.
- **Existing fields reused**:
  - `id`
  - `label`
  - `weekday`
  - `start_time`
  - `end_time`
  - `default_capacity`
  - `is_active`
  - `created_by`
- **New fields**:
  - `session_type` enum `free_practice|course`
  - `default_teacher_id` nullable foreign key to `User`
- **Validation rules**:
  - `session_type` is mandatory
  - une serie `free_practice` ne porte pas de logique de prof obligatoire
  - une serie `course` peut exister sans prof assigne temporairement, mais seul l admin peut la laisser dans cet etat
  - les modifications de serie restent reservees a l admin

### CourseEnrollment

- **Purpose**: represente le rattachement d un adherent a un cours et donc son droit de s inscrire aux occurrences de ce cours.
- **Fields**:
  - `id`
  - `user_id` foreign key to `User`
  - `series_id` foreign key to `SessionSeries`
  - `status` enum `active|removed`
  - `assigned_at`
  - `assigned_by_id` foreign key to `User`
  - `removed_at` nullable
  - `removed_by_id` nullable foreign key to `User`
- **Validation rules**:
  - une inscription de cours active est unique par couple `(user_id, series_id)`
  - `series.session_type` must be `course`
  - le rattachement ne cree jamais automatiquement de reservation d occurrence
- **State transitions**:
  - `active -> removed`

### SessionOccurrence

- **Purpose**: represente une occurrence datee reservable visible dans le calendrier mixte.
- **Existing fields reused**:
  - `id`
  - `series_id`
  - `label`
  - `session_date`
  - `start_time`
  - `end_time`
  - `capacity`
  - `status`
  - `notes`
  - `is_override`
  - `created_by`
  - `created_at`
  - `updated_at`
- **New fields**:
  - `session_type` enum `free_practice|course`
  - `teacher_id` nullable foreign key to `User`
- **Validation rules**:
  - `session_type` is required and is inherited from the series when a series exists
  - une occurrence `course` peut avoir `teacher_id` null temporairement, mais n affiche jamais de logique referent
  - une occurrence `free_practice` ne doit pas exposer de prof dans son detail membre
  - une occurrence `course` n est editable par un prof que si `teacher_id` correspond a l utilisateur courant
  - le type d occurrence reste fixe apres creation pour eviter des migrations metier implicites entre pratiques libres et cours
- **State transitions**:
  - `draft -> open|cancelled`
  - `open -> closed|cancelled|completed`
  - `closed -> open|cancelled|completed`
  - `cancelled` terminal
  - `completed` terminal

### SessionSlot

- **Purpose**: represente un creneau de couverture referent sur une occurrence de pratique libre.
- **Existing fields reused**:
  - `id`
  - `occurrence_id`
  - `sequence_index`
  - `start_time`
  - `end_time`
  - `capacity`
  - `status`
  - `reminder_sent_at`
  - `auto_cancelled_at`
- **Scope rules**:
  - only attached to `SessionOccurrence.session_type = free_practice`
  - never rendered nor managed for course occurrences
- **Validation rules**:
  - les validations existantes de duree et de non-chevauchement restent applicables
  - une occurrence `course` doit avoir zero creneau responsable

### Reservation

- **Purpose**: represente l inscription explicite d un utilisateur a une occurrence autorisee.
- **Existing fields reused**:
  - `id`
  - `occurrence_id`
  - `user_id`
  - `status`
  - `created_by_role`
  - `cancellation_reason`
  - `created_at`
  - `cancelled_at`
- **Validation rules updated**:
  - une reservation active par utilisateur et occurrence reste unique
  - une occurrence `free_practice` n est reservable que si l utilisateur dispose du droit libre correspondant
  - une occurrence `course` n est reservable que si l utilisateur dispose d un `CourseEnrollment` actif pour la serie concernee
  - le rattachement a un cours ne cree jamais de reservation sans action utilisateur explicite
- **State transitions**:
  - `active -> cancelled`

### ResponsibleAssignment

- **Purpose**: represente la couverture active d un creneau de pratique libre par un referent/responsable.
- **Existing fields reused**:
  - `id`
  - `slot_id`
  - `user_id`
  - `assigned_by_user_id`
  - `status`
  - `assigned_at`
  - `released_at`
  - `release_reason`
- **Scope rules**:
  - only valid when `slot.occurrence.session_type = free_practice`
  - never displayed on a course detail panel
- **State transitions**:
  - `active -> released|revoked`

### AuditEntry

- **Purpose**: conserve l historique des actions metier affectant les droits, inscriptions, couvertures et editions d occurrences.
- **Existing fields reused**:
  - `actor_user`
  - `actor_role_snapshot`
  - `action_type`
  - `target_type`
  - `target_id`
  - `occurrence_id`
  - `reservation_id`
  - `slot_id`
  - `responsible_assignment_id`
  - `reason`
  - `metadata_snapshot`
  - `created_at`
- **New action types expected**:
  - `orange_passport_granted`
  - `orange_passport_revoked`
  - `course_enrollment_assigned`
  - `course_enrollment_removed`
  - `course_teacher_assigned`
  - `course_teacher_reassigned`
  - `course_occurrence_updated_by_teacher`
  - existing reservation and responsibility events reused

### OccurrenceAccessPolicy

- **Purpose**: projection derivee en memoire qui decide ce que l utilisateur peut faire sur une occurrence.
- **Fields**:
  - `occurrence_id`
  - `session_type`
  - `can_reserve`
  - `can_cancel`
  - `can_take_responsibility`
  - `can_release_responsibility`
  - `can_edit_as_teacher`
  - `reserve_denial_reason`
- **Validation rules**:
  - une seule raison principale de refus est exposee a l utilisateur pour garder le detail lisible
  - `can_take_responsibility` et `can_release_responsibility` sont toujours `false` pour les cours

## Relationships

- `User 1 -> n CourseEnrollment`
- `SessionSeries 1 -> n CourseEnrollment` only when `session_type = course`
- `SessionSeries 1 -> n SessionOccurrence`
- `SessionSeries 1 -> 0..1 default teacher User`
- `SessionOccurrence n -> 1 SessionSeries`
- `SessionOccurrence 1 -> 0..1 teacher User`
- `SessionOccurrence 1 -> n Reservation`
- `SessionOccurrence 1 -> n SessionSlot` only when `session_type = free_practice`
- `SessionSlot 1 -> n ResponsibleAssignment`
- `SessionOccurrence 1 -> n AuditEntry`
- `Reservation 1 -> n AuditEntry`
- `ResponsibleAssignment 1 -> n AuditEntry`

## Derived Values

- `User.can_book_free_practice = is_active and (has_orange_passport or is_responsable_accredited or is_admin_role)`
- `User.has_course_access(occurrence) = active CourseEnrollment exists for occurrence.series`
- `SessionOccurrence.display_teacher = occurrence.teacher or occurrence.series.default_teacher`
- `SessionOccurrence.requires_responsibility = session_type == free_practice`
- `OccurrenceAccessPolicy.can_reserve` depends on occurrence status, date, remaining capacity and access rule by session type
- `OccurrenceAccessPolicy.can_edit_as_teacher` depends on active teacher ownership and occurrence type `course`

## Migration Notes

- Les occurrences et series existantes doivent recevoir un `session_type` initial `free_practice`.
- Les donnees existantes de creneaux responsables restent rattachees uniquement aux occurrences `free_practice`.
- Les nouveaux cours pourront etre crees soit comme series recurrents, soit comme occurrences isolees de type `course`.
- Aucune reservation existante n a besoin d etre migree vers un nouveau modele, car les inscriptions restent au niveau occurrence.

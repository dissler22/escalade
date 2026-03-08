# Data Model: Vue calendaire hebdomadaire des seances

## Overview

La feature 006 ne change pas le coeur du modele metier. Elle ajoute surtout un modele de presentation derive pour afficher les `SessionOccurrence` existantes dans une grille hebdomadaire et pour concentrer le detail d une seance sous cette grille.

## Existing Domain Entities Reused

### SessionOccurrence

- **Purpose**: represente une seance datee visible par les adherents.
- **Fields reused by the calendar**:
  - `id`
  - `label`
  - `session_date`
  - `start_time`
  - `end_time`
  - `status`
  - `notes`
  - `remaining_capacity`
  - `is_bookable`
  - `coverage_summary`
- **Calendar-specific usage**:
  - sert de source a chaque bloc de seance dans la semaine
  - sert de source au detail inline selectionne

### SessionSlot

- **Purpose**: represente les creneaux de responsabilite d une seance.
- **Fields reused by the inline detail**:
  - `id`
  - `start_time`
  - `end_time`
  - `status`
  - `coverage_status`
  - `current_responsable`
- **Calendar-specific usage**:
  - n est pas affiche en detail dans la grille compacte
  - est affiche dans la zone detaillee sous la semaine

### Reservation

- **Purpose**: represente l inscription de l utilisateur sur la seance selon l implementation actuelle.
- **Fields reused by the inline detail**:
  - `id`
  - `user_id`
  - `status`
- **Calendar-specific usage**:
  - permet de calculer `my_reservation` pour la seance selectionnee
  - ne change pas de schema dans cette feature

### ResponsibleAssignment

- **Purpose**: represente la prise de responsabilite sur un creneau.
- **Fields reused by the inline detail**:
  - `slot_id`
  - `user_id`
  - `status`
- **Calendar-specific usage**:
  - permet de calculer `my_assignment` par creneau dans la zone detaillee

## Presentation Entities

### CalendarWeek

- **Purpose**: represente la semaine actuellement affichee dans le parcours membre.
- **Fields**:
  - `week_start` date, premier jour affiche
  - `week_end` date, dernier jour affiche
  - `visible_start_time` fixed `08:00`
  - `visible_end_time` fixed `23:00`
  - `days` ordered list of `CalendarDay`
  - `previous_week_start`
  - `next_week_start`
  - `selected_occurrence_id` nullable
- **Validation rules**:
  - `week_end = week_start + 6 days`
  - `week_start` doit etre normalise sur le premier jour retenu par l interface
  - la plage visible reste fixe de `08:00` a `23:00`

### CalendarDay

- **Purpose**: represente une colonne de la semaine.
- **Fields**:
  - `date`
  - `label_short`
  - `label_full`
  - `occurrence_blocks` ordered list of `CalendarOccurrenceBlock`
- **Validation rules**:
  - les blocs sont tries par heure de debut puis identifiant stable

### CalendarOccurrenceBlock

- **Purpose**: represente une seance condensee dans la grille.
- **Fields**:
  - `occurrence_id`
  - `display_label_short`
  - `status_label`
  - `start_time`
  - `end_time`
  - `starts_before_visible_range` boolean
  - `ends_after_visible_range` boolean
  - `layout_start_minutes` derived from visible range
  - `layout_duration_minutes` clipped to visible range
  - `overlap_column` derived lane index when two seances overlap the same day
  - `overlap_total` derived lane count for the overlapping group
  - `is_selected`
  - `is_bookable`
  - `remaining_capacity`
  - `coverage_summary`
- **Validation rules**:
  - `layout_start_minutes >= 0`
  - `layout_duration_minutes > 0` only if the seance intersects the visible range
  - le libelle doit rester court et non ambigu pour la semaine affichee

### InlineOccurrenceDetail

- **Purpose**: represente le panneau detail unique affiche sous le calendrier.
- **Fields**:
  - `occurrence_id`
  - `title`
  - `date_label`
  - `time_label`
  - `status_label`
  - `remaining_capacity_label`
  - `coverage_summary_label`
  - `notes`
  - `my_reservation` nullable
  - `slot_cards` ordered list of `InlineSlotCard`
  - `actions` list of available member actions
- **Validation rules**:
  - une seule instance est visible a la fois
  - la detail view doit correspondre a une seance presente dans la semaine affichee ou a la valeur par defaut de selection retenue

### InlineSlotCard

- **Purpose**: represente un creneau responsable dans la zone detaillee.
- **Fields**:
  - `slot_id`
  - `time_label`
  - `coverage_status`
  - `current_responsable_name` nullable
  - `my_assignment` nullable
  - `action_state` enum `none|take|release`
- **Validation rules**:
  - `action_state` depend uniquement du role utilisateur, de l etat du creneau et de l affectation courante

### CalendarPageState

- **Purpose**: encapsule l etat complet rendu par la page `/sessions/`.
- **Fields**:
  - `week` as `CalendarWeek`
  - `selected_detail` nullable `InlineOccurrenceDetail`
  - `empty_state_message`
  - `flash_messages`
- **Validation rules**:
  - le detail est `null` si la semaine ne contient aucune seance
  - sinon le detail pointe vers la seance selectionnee ou, a defaut, vers la premiere seance de la semaine retenue par la page

## Relationships

- `CalendarPageState 1 -> 1 CalendarWeek`
- `CalendarWeek 1 -> 7 CalendarDay`
- `CalendarDay 1 -> n CalendarOccurrenceBlock`
- `CalendarPageState 1 -> 0..1 InlineOccurrenceDetail`
- `InlineOccurrenceDetail 1 -> n InlineSlotCard`
- `CalendarOccurrenceBlock n -> 1 SessionOccurrence`
- `InlineOccurrenceDetail 1 -> 1 SessionOccurrence`
- `InlineSlotCard n -> 1 SessionSlot`

## Derived Values

- `week_start` is derived from the request query parameter or the current date.
- `selected_occurrence_id` is derived from the request query parameter or the first occurrence in the visible week.
- `display_label_short` is derived from `SessionOccurrence.label` with calendar-specific shortening rules.
- `status_label` is derived from `SessionOccurrence.status`, `remaining_capacity` and `coverage_summary`.
- `layout_start_minutes` and `layout_duration_minutes` are derived from the intersection between the seance times and the fixed visible range `08:00-23:00`.
- `overlap_column` and `overlap_total` are derived from same-day overlaps so blocks remain distinguishable when schedules collide.
- `InlineOccurrenceDetail.actions` is derived from current user role plus existing booking and responsibility eligibility rules.

## State Transitions

### Calendar Navigation State

- `initial load -> selected week resolved`
- `selected week resolved -> selected occurrence resolved`
- `selected occurrence resolved -> inline detail rendered`
- `post action redirect -> same week resolved again -> same occurrence reselected`

### Action Feedback State

- `idle -> booking submitted -> redirect with success or error message`
- `idle -> cancellation submitted -> redirect with success or error message`
- `idle -> responsibility submitted -> redirect with success or error message`

## Persistence Impact

- Aucun nouveau modele persistant n est requis pour cette feature.
- Aucun changement de schema n est attendu si la vue semaine est entierement derivee des entites existantes.
- Les evolutions attendues portent sur les vues, les services de presentation, les templates, les routes et les tests.

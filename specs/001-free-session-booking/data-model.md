# Data Model - Reservations de seances libres

## 1. CompteUtilisateur

### Purpose

Represente une personne autorisee a acceder a l'application et a agir selon son role.

### Fields

- `id`: identifiant unique
- `full_name`: nom affiche
- `email`: email unique de connexion
- `role`: `member` ou `admin`
- `is_active`: indique si le compte peut encore se connecter et reserver
- `password_state`: temporaire, active ou a reinitialiser
- `created_at`
- `updated_at`

### Validation Rules

- `email` doit etre unique.
- Un compte inactif ne peut ni se connecter ni reserver.
- Un compte `member` ne peut effectuer aucune action reservee a `admin`.

### Relationships

- Un `CompteUtilisateur` peut avoir plusieurs `Reservation`.
- Un `CompteUtilisateur` peut etre acteur de plusieurs `TraceAudit`.

## 2. SerieSeance

### Purpose

Represente un modele hebdomadaire reutilisable pour preparer les seances libres recurrentes.

### Fields

- `id`
- `label`: nom court visible cote admin
- `weekday`: jour de semaine
- `start_time`
- `end_time`
- `default_capacity`
- `is_active`
- `created_by`
- `created_at`
- `updated_at`

### Validation Rules

- `default_capacity` doit etre strictement positif.
- `end_time` doit etre posterieur a `start_time`.
- La desactivation d'une serie n'annule pas automatiquement les occurrences deja creees.

### Relationships

- Une `SerieSeance` peut produire plusieurs `OccurrenceSeance`.
- Une `SerieSeance` reference un `CompteUtilisateur` createur.

## 3. OccurrenceSeance

### Purpose

Represente une date concrete reservable par les adherents.

### Fields

- `id`
- `series_id`: optionnel si la seance est ponctuelle
- `label`: nom ou resume visible aux utilisateurs
- `session_date`
- `start_time`
- `end_time`
- `capacity`
- `status`: `draft`, `open`, `closed`, `cancelled`, `completed`
- `notes`: commentaire admin optionnel
- `created_by`
- `created_at`
- `updated_at`

### Validation Rules

- `capacity` doit etre strictement positif.
- `session_date + start_time` doit etre dans le futur pour autoriser une nouvelle reservation.
- Une occurrence `cancelled` n'accepte aucune reservation.
- Une occurrence `closed` n'accepte aucune reservation supplementaire mais conserve ses inscriptions existantes.
- Une diminution de `capacity` en dessous du nombre de reservations actives doit etre bloquee ou explicitement geree par l'admin avant validation.

### Relationships

- Une `OccurrenceSeance` peut appartenir a zero ou une `SerieSeance`.
- Une `OccurrenceSeance` a plusieurs `Reservation`.
- Une `OccurrenceSeance` a plusieurs `TraceAudit`.

### State Transitions

- `draft -> open`
- `draft -> cancelled`
- `open -> closed`
- `open -> cancelled`
- `closed -> open`
- `closed -> cancelled`
- `open|closed|cancelled -> completed` seulement apres la date de seance

## 4. Reservation

### Purpose

Represente la prise ou la liberation d'une place par un adherent sur une occurrence.

### Fields

- `id`
- `occurrence_id`
- `user_id`
- `status`: `active`, `cancelled`
- `created_by_role`: `member` ou `admin`
- `cancellation_reason`: optionnel
- `created_at`
- `cancelled_at`: optionnel

### Validation Rules

- Une seule reservation `active` par couple `user_id + occurrence_id`.
- Une reservation `active` ne peut etre creee que si l'occurrence est `open`, future et non complete.
- Une reservation annulee n'est jamais physiquement reutilisee comme si elle etait active.
- Une reservation retiree par admin doit laisser une `TraceAudit`.

### Relationships

- Une `Reservation` appartient a une `OccurrenceSeance`.
- Une `Reservation` appartient a un `CompteUtilisateur`.
- Une `Reservation` peut etre referencee par plusieurs `TraceAudit`.

## 5. TraceAudit

### Purpose

Represente une action horodatee utile a la reprise d'incident et a l'explication des etats.

### Fields

- `id`
- `actor_user_id`
- `actor_role_snapshot`
- `action_type`
- `target_type`
- `target_id`
- `occurrence_id`: optionnel mais renseigne des que l'action impacte une seance
- `reservation_id`: optionnel
- `reason`: optionnel
- `metadata_snapshot`: donnees minimales utiles a l'explication
- `created_at`

### Validation Rules

- Toute creation, modification, ouverture, fermeture, annulation ou correction manuelle touchant une seance doit creer une trace.
- Une trace d'audit ne doit pas etre supprimee par un changement d'etat courant.

### Relationships

- Une `TraceAudit` peut pointer vers un `CompteUtilisateur`, une `OccurrenceSeance`, une `Reservation` ou une `SerieSeance`.

## Concurrency Rules

- La verification de disponibilite et la creation d'une reservation active doivent etre traitees comme une operation unique afin d'eviter de depasser la capacite sur la derniere place.
- Toute correction admin doit recalculer la disponibilite effective de l'occurrence avant confirmation.

## Derived Values

- `remaining_capacity = capacity - count(reservations active)`
- `is_bookable = status == open && start_datetime > now && remaining_capacity > 0`

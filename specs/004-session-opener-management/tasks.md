# Tasks: Gestion des responsables de pratique libre

**Input**: Design documents from `/specs/004-session-opener-management/`
**Prerequisites**: [plan.md](/home/marius/work/repos/escalade/specs/004-session-opener-management/plan.md), [spec.md](/home/marius/work/repos/escalade/specs/004-session-opener-management/spec.md), [research.md](/home/marius/work/repos/escalade/specs/004-session-opener-management/research.md), [data-model.md](/home/marius/work/repos/escalade/specs/004-session-opener-management/data-model.md), [openapi.yaml](/home/marius/work/repos/escalade/specs/004-session-opener-management/contracts/openapi.yaml)

**Tests**: Inclure des tests unitaires, integration et contrat pour les regles de slot, de responsabilite, de trace d audit et d automatisation J-7/J-2. Les memoires `.specify/memory/product.md` et `.specify/memory/test-registry.md` sont absentes du repo; reutiliser la suite pytest existante.

**Organization**: Les taches sont groupees par user story pour conserver un increment testable independamment, avec MVP manuel avant l automatisation email.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut etre executee en parallele
- **[Story]**: User story concernee (`[US1]`, `[US2]`, `[US3]`)
- Chaque tache cite les fichiers exacts a modifier ou creer

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Poser les points d entree communs pour la feature et ses tests

- [X] T001 [P] Etendre la regression de contrat pour la feature 004 dans `/home/marius/work/repos/escalade/tests/contract/test_openapi_contract.py`
- [X] T002 Creer le squelette des commandes planifiees dans `/home/marius/work/repos/escalade/src/sessions/management/__init__.py` et `/home/marius/work/repos/escalade/src/sessions/management/commands/__init__.py`
- [X] T003 [P] Ajouter la configuration de l expediteur email applicatif dans `/home/marius/work/repos/escalade/src/config/env.py` et `/home/marius/work/repos/escalade/src/config/settings.py`
- [X] T004 [P] Etendre les fixtures partagees pour comptes admin/responsable, seances parent et slots dans `/home/marius/work/repos/escalade/tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Mettre en place le modele de donnees, les permissions et la tracabilite communs a toutes les stories

**CRITICAL**: Aucune user story ne commence avant la fin de cette phase

- [X] T005 Creer le schema slot/responsable et les migrations de backfill dans `/home/marius/work/repos/escalade/src/accounts/models.py`, `/home/marius/work/repos/escalade/src/sessions/models.py`, `/home/marius/work/repos/escalade/src/bookings/models.py`, `/home/marius/work/repos/escalade/src/audit/models.py`, `/home/marius/work/repos/escalade/src/accounts/migrations/0002_responsable_accreditation.py`, `/home/marius/work/repos/escalade/src/sessions/migrations/0002_session_slots.py`, `/home/marius/work/repos/escalade/src/bookings/migrations/0002_slot_reservations.py` et `/home/marius/work/repos/escalade/src/audit/migrations/0002_slot_audit_context.py`
- [X] T006 [P] Refondre les requetes partagees pour exposer seances parent, resumes de couverture et detail de slots dans `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/sessions/views.py`
- [X] T007 [P] Refondre les services de reservation pour travailler au niveau du slot au lieu de l occurrence dans `/home/marius/work/repos/escalade/src/bookings/services.py` et `/home/marius/work/repos/escalade/src/bookings/views.py`
- [X] T008 [P] Etendre l audit pour les slots, affectations responsable et annulations ciblees dans `/home/marius/work/repos/escalade/src/audit/services.py`, `/home/marius/work/repos/escalade/src/audit/views.py` et `/home/marius/work/repos/escalade/src/audit/urls.py`
- [X] T009 [P] Uniformiser les controles d acces admin et responsable dans `/home/marius/work/repos/escalade/src/accounts/views_admin.py`, `/home/marius/work/repos/escalade/src/sessions/views_admin.py` et `/home/marius/work/repos/escalade/src/bookings/views_admin.py`
- [X] T010 Documenter la reprise manuelle des creneaux non couverts ou annules dans `/home/marius/work/repos/escalade/specs/004-session-opener-management/quickstart.md`

**Checkpoint**: Le socle slot/responsable est en place, trace et exploitable manuellement

---

## Phase 3: User Story 1 - Prendre un creneau comme responsable depuis son telephone (Priority: P1) MVP

**Goal**: Permettre a un responsable accredite de prendre ou quitter la responsabilite d un slot futur depuis un parcours mobile, tout en conservant l inscription pratiquant distincte

**Independent Test**: Avec des slots futurs deja crees et un utilisateur accredite responsable, le membre se connecte sur smartphone, prend un slot sans responsable, voit qu un second responsable est refuse, puis quitte son role sans perdre une inscription pratiquant deja existante sur ce meme slot.

### Tests for User Story 1

- [X] T011 [P] [US1] Ajouter la couverture unitaire des prises et abandons de responsabilite dans `/home/marius/work/repos/escalade/tests/unit/test_slot_responsibility_service.py`
- [X] T012 [P] [US1] Ajouter le parcours integration membre/responsable mobile dans `/home/marius/work/repos/escalade/tests/integration/test_member_responsable_flow.py`

### Implementation for User Story 1

- [X] T013 [US1] Implementer la prise et le retrait de responsabilite sur un slot futur dans `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/sessions/views.py`
- [X] T014 [US1] Ajouter les routes de responsabilite et les identifiants de slot dans `/home/marius/work/repos/escalade/src/sessions/urls.py` et `/home/marius/work/repos/escalade/src/bookings/urls.py`
- [X] T015 [US1] Adapter les actions de reservation pour conserver la separation reservation pratiquant vs responsabilite dans `/home/marius/work/repos/escalade/src/bookings/services.py` et `/home/marius/work/repos/escalade/src/bookings/views.py`
- [X] T016 [US1] Mettre a jour les ecrans mobile des seances et reservations avec statut de couverture et CTA responsable dans `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`, `/home/marius/work/repos/escalade/src/templates/sessions/session_detail.html` et `/home/marius/work/repos/escalade/src/templates/bookings/my_reservations.html`
- [X] T017 [US1] Emettre les traces d audit et messages utilisateur pour prise, refus et abandon de responsabilite dans `/home/marius/work/repos/escalade/src/audit/services.py` et `/home/marius/work/repos/escalade/src/templates/sessions/session_detail.html`
- [X] T018 [US1] Ajuster le rendu smartphone des listes de slots et badges de couverture dans `/home/marius/work/repos/escalade/src/static/css/app.css`, `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html` et `/home/marius/work/repos/escalade/src/templates/sessions/session_detail.html`

**Checkpoint**: Le parcours responsable mobile est demonstrable et testable independamment sur des donnees deja preparees

---

## Phase 4: User Story 2 - Preparer les seances et accrediter les responsables (Priority: P2)

**Goal**: Donner a l administrateur les moyens d accrediter les responsables, creer des seances longues, generer automatiquement les slots de 90 minutes max et corriger manuellement les affectations

**Independent Test**: Un administrateur accredite un adherent comme responsable, cree une seance de 3 heures, constate le decoupage automatique en slots de 90 minutes max, puis retire une accreditation ou reaffecte manuellement un responsable sur un slot futur.

### Tests for User Story 2

- [X] T019 [P] [US2] Ajouter la couverture integration des accreditations responsable et de leur retrait futur dans `/home/marius/work/repos/escalade/tests/integration/test_admin_responsable_management.py`
- [X] T020 [P] [US2] Ajouter la couverture unitaire du decoupage automatique des seances en slots dans `/home/marius/work/repos/escalade/tests/unit/test_session_slot_generation.py`

### Implementation for User Story 2

- [X] T021 [US2] Ajouter l accreditation responsable et son edition admin dans `/home/marius/work/repos/escalade/src/accounts/models.py`, `/home/marius/work/repos/escalade/src/accounts/views_admin.py`, `/home/marius/work/repos/escalade/src/accounts/urls_admin.py` et `/home/marius/work/repos/escalade/src/templates/admin/accounts/account_list.html`
- [X] T022 [US2] Implementer la creation et la mise a jour de seances parent avec generation automatique de slots dans `/home/marius/work/repos/escalade/src/sessions/forms.py`, `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/sessions/views_admin.py`
- [X] T023 [US2] Ajouter l affectation et le retrait manuel d un responsable par l admin dans `/home/marius/work/repos/escalade/src/sessions/views_admin.py` et `/home/marius/work/repos/escalade/src/sessions/urls_admin.py`
- [X] T024 [US2] Mettre a jour les ecrans admin des seances pour afficher couverture, slots, statuts et actions de correction dans `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_list.html` et `/home/marius/work/repos/escalade/src/templates/admin/sessions/occurrence_form.html`
- [X] T025 [US2] Adapter la correction manuelle des reservations au niveau des slots et aux gardes sur creneaux annules dans `/home/marius/work/repos/escalade/src/bookings/views_admin.py`, `/home/marius/work/repos/escalade/src/bookings/urls_admin.py` et `/home/marius/work/repos/escalade/src/templates/admin/bookings/session_reservations.html`
- [X] T026 [US2] Etendre l historique admin pour les accreditations, editions de slots et corrections manuelles de responsable dans `/home/marius/work/repos/escalade/src/audit/views.py` et `/home/marius/work/repos/escalade/src/templates/admin/audit/session_history.html`

**Checkpoint**: L administration peut preparer le planning, accrediter les responsables et corriger manuellement un slot sans automatisme

---

## Phase 5: User Story 3 - Relancer puis annuler automatiquement les creneaux non couverts (Priority: P3)

**Goal**: Automatiser le rappel J-7, l annulation ciblee J-2 et l information des inscrits, tout en gardant une reprise manuelle simple pour l admin

**Independent Test**: Avec des slots futurs non couverts et une configuration email de test, l execution du traitement planifie envoie un rappel a J-7, annule uniquement le slot non couvert a J-2, notifie les inscrits concernes et laisse les autres slots de la meme seance inchanges.

### Tests for User Story 3

- [X] T027 [P] [US3] Ajouter la couverture unitaire des echeances J-7 et J-2 dans `/home/marius/work/repos/escalade/tests/unit/test_slot_coverage_deadlines.py`
- [X] T028 [P] [US3] Ajouter la couverture integration de l expediteur visible et des notifications d annulation dans `/home/marius/work/repos/escalade/tests/integration/test_slot_notification_flow.py`

### Implementation for User Story 3

- [X] T029 [US3] Implementer la configuration de l expediteur et son affichage admin dans `/home/marius/work/repos/escalade/src/config/env.py`, `/home/marius/work/repos/escalade/src/config/settings.py`, `/home/marius/work/repos/escalade/src/accounts/views_admin.py` et `/home/marius/work/repos/escalade/src/templates/admin/accounts/account_list.html`
- [X] T030 [US3] Implementer les services de rappel J-7, annulation J-2 et notification ciblee avec audit dans `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/audit/services.py`
- [X] T031 [US3] Ajouter la commande planifiee de traitement des slots non couverts dans `/home/marius/work/repos/escalade/src/sessions/management/commands/process_slot_coverage_deadlines.py`
- [X] T032 [US3] Exposer dans l administration les creneaux non couverts, annules et l adresse d envoi active pour reprise manuelle dans `/home/marius/work/repos/escalade/src/sessions/views_admin.py`, `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_list.html` et `/home/marius/work/repos/escalade/src/templates/admin/audit/session_history.html`
- [X] T033 [US3] Completer la procedure de secours quotidienne et le mode d execution manuel du scheduler dans `/home/marius/work/repos/escalade/specs/004-session-opener-management/quickstart.md`

**Checkpoint**: Les rappels et annulations automatiques fonctionnent sans supprimer la reprise manuelle admin

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finaliser le contrat, la validation bout en bout et les regressions transverses

- [X] T034 [P] Mettre a jour le contrat de reference livre avec les routes et schemas definitifs dans `/home/marius/work/repos/escalade/specs/004-session-opener-management/contracts/openapi.yaml`
- [X] T035 Revalider la minimisation des donnees et les acces admin/responsable dans `/home/marius/work/repos/escalade/specs/004-session-opener-management/data-model.md` et `/home/marius/work/repos/escalade/specs/004-session-opener-management/quickstart.md`
- [X] T036 [P] Executer et documenter la validation smartphone + reprise manuelle de bout en bout dans `/home/marius/work/repos/escalade/specs/004-session-opener-management/quickstart.md`
- [X] T037 Consolider la regression finale pytest/contrat pour la feature dans `/home/marius/work/repos/escalade/tests/contract/test_openapi_contract.py`, `/home/marius/work/repos/escalade/tests/integration/test_member_responsable_flow.py`, `/home/marius/work/repos/escalade/tests/integration/test_admin_responsable_management.py` et `/home/marius/work/repos/escalade/tests/integration/test_slot_notification_flow.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: aucune dependance, demarre immediatement
- **Phase 2: Foundational**: depend de la phase 1 et bloque toutes les stories
- **Phase 3: US1**: depend de la phase 2
- **Phase 4: US2**: depend de la phase 2
- **Phase 5: US3**: depend des phases 2 et 4, puis reutilise le socle manuel deja livre
- **Phase 6: Polish**: depend des stories retenues pour la livraison

### User Story Dependencies

- **US1**: premier increment MVP sur smartphone, testable avec des slots deja prepares
- **US2**: complete le MVP operable club en donnant le vrai pilotage admin des slots et accreditations
- **US3**: ne commence qu apres la baseline manuelle admin/responsable, conformement a la constitution

### Within Each User Story

- Ecrire les tests de la story avant ou en meme temps que l implementation a risque
- Poser d abord les services et validations metier
- Brancher ensuite routes, vues et templates
- Finaliser la story avec audit, validation smartphone et reprise manuelle

### Suggested Completion Order

1. Phase 1
2. Phase 2
3. Phase 3 (US1) pour le MVP mobile
4. Phase 4 (US2) pour rendre la feature exploitable par le club
5. Phase 5 (US3) pour l automatisation email
6. Phase 6

---

## Parallel Opportunities

- Les taches `T001`, `T003` et `T004` peuvent avancer en parallele pendant la phase 1
- Les taches `T006`, `T007`, `T008` et `T009` peuvent avancer en parallele apres `T005`
- Dans `US1`, `T011` et `T012` peuvent demarrer en parallele pendant que `T013` pose les services
- Dans `US2`, `T019` et `T020` peuvent demarrer en parallele; `T024` et `T026` peuvent ensuite etre menes en parallele une fois `T021` a `T023` stabilisees
- Dans `US3`, `T027` et `T028` peuvent demarrer en parallele; `T031` et `T033` peuvent etre menees en parallele apres `T030`

---

## Parallel Example: User Story 1

```bash
Task: "Ajouter la couverture unitaire des prises et abandons de responsabilite dans tests/unit/test_slot_responsibility_service.py"
Task: "Ajouter le parcours integration membre/responsable mobile dans tests/integration/test_member_responsable_flow.py"

Task: "Mettre a jour les ecrans mobile des seances et reservations dans src/templates/sessions/session_list.html, src/templates/sessions/session_detail.html et src/templates/bookings/my_reservations.html"
Task: "Ajuster le rendu smartphone des listes de slots et badges de couverture dans src/static/css/app.css"
```

## Parallel Example: User Story 2

```bash
Task: "Ajouter la couverture integration des accreditations responsable dans tests/integration/test_admin_responsable_management.py"
Task: "Ajouter la couverture unitaire du decoupage automatique des seances en slots dans tests/unit/test_session_slot_generation.py"

Task: "Mettre a jour les ecrans admin des seances dans src/templates/admin/sessions/series_list.html et src/templates/admin/sessions/occurrence_form.html"
Task: "Etendre l historique admin dans src/audit/views.py et src/templates/admin/audit/session_history.html"
```

## Parallel Example: User Story 3

```bash
Task: "Ajouter la couverture unitaire des echeances J-7 et J-2 dans tests/unit/test_slot_coverage_deadlines.py"
Task: "Ajouter la couverture integration de l expediteur visible et des notifications d annulation dans tests/integration/test_slot_notification_flow.py"

Task: "Ajouter la commande planifiee dans src/sessions/management/commands/process_slot_coverage_deadlines.py"
Task: "Completer la procedure de secours quotidienne dans specs/004-session-opener-management/quickstart.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Terminer la phase 1
2. Terminer la phase 2
3. Livrer la phase 3 pour le parcours responsable mobile
4. Verifier smartphone, audit et refus du double responsable

### Club-Operable Baseline

1. Ajouter la phase 4 juste apres US1
2. Valider accreditation admin, generation automatique des slots et corrections manuelles
3. Demarrer l utilisation reelle sans dependre des emails automatiques

### Incremental Delivery

1. Setup + Foundational
2. US1
3. US2
4. US3
5. Polish

### Parallel Team Strategy

1. Toute l equipe ferme les phases 1 et 2
2. Puis:
   Developer A: US1
   Developer B: US2
   Developer C: US3 apres stabilisation de US2

---

## Notes

- Toutes les taches respectent le format checklist `- [ ] T### ...`
- Les automatisations email restent apres la baseline manuelle admin/responsable
- Les specs `001-free-session-booking` et `002-gcp-vm-deploy` restent les invariants de reservation et d exploitation VM
- Les memoires `.specify/memory/product.md` et `.specify/memory/test-registry.md` sont absentes du repo au moment de la generation

# Tasks: Rafraichissement visuel USMV

**Input**: Design documents from `/home/marius/work/repos/escalade/specs/003-club-visual-refresh/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

**Tests**: Inclure des tests d'integration et de contrat sur cette feature est justifie par le risque de regression visuelle sur des parcours metier existants et par l'exigence explicite de prouver l'absence de regression fonctionnelle.

**Organization**: Les taches sont groupees par user story pour livrer d'abord le socle membre mobile, puis les ecrans admin, puis la validation complete de la refonte purement visuelle.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut etre executee en parallele (fichiers differents, pas de dependance sur une tache incomplete)
- **[Story]**: User story concernee (`[US1]`, `[US2]`, `[US3]`)
- Chaque tache contient un chemin de fichier exact

## Phase 1: Setup (Shared Review Scope)

**Purpose**: Verrouiller le perimetre de revue, les ecrans cibles et la procedure manuelle avant la mise a jour des templates

- [X] T001 Mettre a jour la matrice de revue ecran par ecran et les criteres smartphone dans `/home/marius/work/repos/escalade/specs/003-club-visual-refresh/quickstart.md`
- [X] T002 [P] Completer la cartographie ecran -> composants visuels partages dans `/home/marius/work/repos/escalade/specs/003-club-visual-refresh/data-model.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Mettre en place le shell visuel et les composants partages qui bloquent toutes les stories

**CRITICAL**: Aucun travail de story ne doit commencer avant la fin de cette phase

- [X] T003 [P] Mettre a jour le shell commun, la zone de marque, le contexte de role et la structure des messages dans `/home/marius/work/repos/escalade/src/templates/base.html`
- [X] T004 [P] Mettre a jour les tokens USMV, la typographie, les variantes de boutons, formulaires, badges, tableaux et utilitaires responsives dans `/home/marius/work/repos/escalade/src/static/css/app.css`

**Checkpoint**: Le shell partage et la feuille de style commune sont prets pour les stories membre et admin

---

## Phase 3: User Story 1 - Reconnaitre immediatement l'univers du club sur smartphone (Priority: P1) MVP

**Goal**: Rendre les ecrans adherent immediatement reconnaissables comme un service USMV Escalade sans changer les actions de connexion, consultation, reservation et annulation

**Independent Test**: Depuis un smartphone, un adherent se connecte via `/login/`, parcourt `/sessions/`, ouvre `/sessions/<occurrence_id>/`, puis consulte `/bookings/mine/` et retrouve les actions existantes avec une charte visuelle coherente

### Tests for User Story 1

- [X] T005 [P] [US1] Etendre les assertions de parcours membre et de libelles d'action conserves dans `/home/marius/work/repos/escalade/tests/integration/test_member_booking_flow.py`
- [X] T006 [P] [US1] Etendre les assertions de connexion et d'acces a la page login dans `/home/marius/work/repos/escalade/tests/integration/test_accounts_access.py`

### Implementation for User Story 1

- [X] T007 [US1] Rafraichir l'ecran de connexion avec branding club et hierarchie du formulaire dans `/home/marius/work/repos/escalade/src/templates/accounts/login.html`
- [X] T008 [US1] Rafraichir les cartes de liste, les metas et les reperes de navigation membre dans `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`
- [X] T009 [US1] Rafraichir la hierarchie statut/action de la fiche seance dans `/home/marius/work/repos/escalade/src/templates/sessions/session_detail.html`
- [X] T010 [US1] Rafraichir la presentation des reservations personnelles et du controle d'annulation dans `/home/marius/work/repos/escalade/src/templates/bookings/my_reservations.html`

**Checkpoint**: Le parcours membre mobile est complet, testable et livrable comme MVP

---

## Phase 4: User Story 2 - Utiliser des ecrans d'administration alignes avec le reste de l'application (Priority: P2)

**Goal**: Harmoniser les ecrans admin denses avec la charte commune tout en conservant les formulaires, tableaux et actions de gestion existants

**Independent Test**: Un administrateur ouvre `/admin/sessions/`, `/admin/sessions/series/new/`, `/admin/sessions/occurrences/new/`, `/admin/bookings/sessions/<occurrence_id>/`, `/admin/accounts/` et `/admin/audit/sessions/<occurrence_id>/` sur smartphone puis desktop, et retrouve des ecrans lisibles avec les memes controles metier qu'avant

### Tests for User Story 2

- [X] T011 [P] [US2] Etendre la couverture du tableau de bord et des formulaires admin dans `/home/marius/work/repos/escalade/tests/integration/test_admin_session_management.py`
- [X] T012 [P] [US2] Etendre la couverture des corrections de reservations admin dans `/home/marius/work/repos/escalade/tests/integration/test_admin_booking_corrections.py`
- [X] T013 [P] [US2] Etendre la couverture des permissions et de la navigation admin dans `/home/marius/work/repos/escalade/tests/integration/test_admin_permissions.py`

### Implementation for User Story 2

- [X] T014 [US2] Rafraichir le tableau de bord admin des series et occurrences dans `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_list.html`
- [X] T015 [P] [US2] Rafraichir la presentation du formulaire de serie hebdomadaire dans `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_form.html`
- [X] T016 [P] [US2] Rafraichir la presentation du formulaire d'occurrence et du bloc de statut dans `/home/marius/work/repos/escalade/src/templates/admin/sessions/occurrence_form.html`
- [X] T017 [P] [US2] Rafraichir l'ecran de corrections manuelles des reservations dans `/home/marius/work/repos/escalade/src/templates/admin/bookings/session_reservations.html`
- [X] T018 [P] [US2] Rafraichir le tableau de gestion des comptes et les controles inline dans `/home/marius/work/repos/escalade/src/templates/admin/accounts/account_list.html`
- [X] T019 [US2] Rafraichir la chronologie d'audit et la lisibilite des traces dans `/home/marius/work/repos/escalade/src/templates/admin/audit/session_history.html`

**Checkpoint**: Les ecrans admin sont coherents avec le parcours membre et restent exploitables en densite forte

---

## Phase 5: User Story 3 - Valider une refonte purement visuelle sans regression metier (Priority: P3)

**Goal**: Prouver que la refonte reste purement visuelle via des artefacts de validation, un contrat a jour et une revue manuelle finie

**Independent Test**: Les parcours membre et admin existants restent jouables avec succes, le contrat de la feature couvre les pages revuees et la checklist manuelle permet de confirmer que seules la presentation et la hierarchie visuelle ont change

### Tests for User Story 3

- [X] T020 [P] [US3] Ajouter une revue d'integration consolidee des marqueurs visuels membre/admin dans `/home/marius/work/repos/escalade/tests/integration/test_visual_refresh_review.py`
- [X] T021 [P] [US3] Etendre les assertions de contrat pour la feature 003 dans `/home/marius/work/repos/escalade/tests/contract/test_openapi_contract.py`

### Implementation for User Story 3

- [X] T022 [US3] Mettre a jour le contrat de revue visuelle des pages HTML et de `/static/css/app.css` dans `/home/marius/work/repos/escalade/specs/003-club-visual-refresh/contracts/openapi.yaml`
- [X] T023 [US3] Finaliser la procedure de validation manuelle et de repli visuel dans `/home/marius/work/repos/escalade/specs/003-club-visual-refresh/quickstart.md`

**Checkpoint**: La refonte est prouvable comme purement visuelle et sans regression metier attendue

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finaliser la coherence transversale, les risques residuels et la verification de repli

- [X] T024 [P] Consolider les decisions finales de design et les risques residuels dans `/home/marius/work/repos/escalade/specs/003-club-visual-refresh/research.md`
- [X] T025 Valider la coherence transversale des fallback visuels et des messages partages dans `/home/marius/work/repos/escalade/src/templates/base.html` et `/home/marius/work/repos/escalade/src/static/css/app.css`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 - Setup**: aucune dependance, peut commencer immediatement
- **Phase 2 - Foundational**: depend de la Phase 1 et bloque toutes les stories
- **Phase 3 - US1**: depend de la Phase 2 et constitue le MVP
- **Phase 4 - US2**: depend de la Phase 2, mais doit rester coherente avec le shell livre en US1
- **Phase 5 - US3**: depend de la completion de US1 et US2 pour valider la totalite du perimetre
- **Phase 6 - Polish**: depend de toutes les stories visees

### User Story Dependencies

- **US1 (P1)**: commence en premier parce qu'elle couvre le parcours coeur adherent et la reconnaissance de marque
- **US2 (P2)**: peut demarrer apres le socle partage, mais doit s'aligner sur les composants et reperes poses pour US1
- **US3 (P3)**: commence apres US1 et US2, car elle consolide la preuve de non-regression et les artefacts de validation

### Within Each User Story

- Les tests de la story passent avant les ajustements de template et de contrat
- Les mises a jour de template viennent apres le socle partage
- La story est terminee seulement quand le parcours independant defini plus haut est rejouable

### Parallel Opportunities

- `T001` et `T002` peuvent avancer en parallele
- `T003` et `T004` peuvent avancer en parallele
- En US1, `T005` et `T006` peuvent avancer en parallele
- En US2, `T011`, `T012`, `T013`, `T015`, `T016`, `T017` et `T018` peuvent etre reparties entre plusieurs personnes
- En US3, `T020` et `T021` peuvent avancer en parallele pendant la mise a jour du contrat et de la quickstart

---

## Parallel Example: User Story 1

```bash
Task: "Etendre les assertions de parcours membre et de libelles d'action conserves dans /home/marius/work/repos/escalade/tests/integration/test_member_booking_flow.py"
Task: "Etendre les assertions de connexion et d'acces a la page login dans /home/marius/work/repos/escalade/tests/integration/test_accounts_access.py"

Task: "Rafraichir les cartes de liste, les metas et les reperes de navigation membre dans /home/marius/work/repos/escalade/src/templates/sessions/session_list.html"
Task: "Rafraichir la presentation des reservations personnelles et du controle d'annulation dans /home/marius/work/repos/escalade/src/templates/bookings/my_reservations.html"
```

---

## Parallel Example: User Story 2

```bash
Task: "Etendre la couverture du tableau de bord et des formulaires admin dans /home/marius/work/repos/escalade/tests/integration/test_admin_session_management.py"
Task: "Etendre la couverture des corrections de reservations admin dans /home/marius/work/repos/escalade/tests/integration/test_admin_booking_corrections.py"
Task: "Etendre la couverture des permissions et de la navigation admin dans /home/marius/work/repos/escalade/tests/integration/test_admin_permissions.py"

Task: "Rafraichir la presentation du formulaire de serie hebdomadaire dans /home/marius/work/repos/escalade/src/templates/admin/sessions/series_form.html"
Task: "Rafraichir la presentation du formulaire d'occurrence et du bloc de statut dans /home/marius/work/repos/escalade/src/templates/admin/sessions/occurrence_form.html"
Task: "Rafraichir le tableau de gestion des comptes et les controles inline dans /home/marius/work/repos/escalade/src/templates/admin/accounts/account_list.html"
```

---

## Parallel Example: User Story 3

```bash
Task: "Ajouter une revue d'integration consolidee des marqueurs visuels membre/admin dans /home/marius/work/repos/escalade/tests/integration/test_visual_refresh_review.py"
Task: "Etendre les assertions de contrat pour la feature 003 dans /home/marius/work/repos/escalade/tests/contract/test_openapi_contract.py"

Task: "Mettre a jour le contrat de revue visuelle des pages HTML et de /static/css/app.css dans /home/marius/work/repos/escalade/specs/003-club-visual-refresh/contracts/openapi.yaml"
Task: "Finaliser la procedure de validation manuelle et de repli visuel dans /home/marius/work/repos/escalade/specs/003-club-visual-refresh/quickstart.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completer la Phase 1
2. Completer la Phase 2
3. Completer la Phase 3 (US1)
4. Rejouer le test independant de US1 sur smartphone
5. Livrer ou faire valider le MVP avant d'etendre aux ecrans admin

### Incremental Delivery

1. Setup + Foundational pour figer le systeme visuel partage
2. US1 pour livrer le parcours membre
3. US2 pour aligner l'administration sur la meme charte
4. US3 pour prouver l'absence de regression metier et clore la revue
5. Polish pour harmoniser les fallback et la documentation finale

### Parallel Team Strategy

1. Une personne peut traiter `T003` pendant qu'une autre traite `T004`
2. Une fois le socle partage termine, les tests de story peuvent etre ouverts en parallele avec les updates de templates sur des fichiers distincts
3. US2 peut etre decoupee par groupes d'ecrans admin: dashboard, formulaires, corrections, comptes, audit

---

## Notes

- `.specify/memory/product.md` est absent du depot
- `.specify/memory/test-registry.md` est absent du depot
- Le scope de ces taches reste strictement visuel: aucune tache ne change les services metier, les permissions ou les traces attendues par `001-free-session-booking`

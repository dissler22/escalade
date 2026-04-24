# Tasks: Types de seance et droits d acces

**Input**: Design documents from `/home/marius/work/repos/escalade/specs/007-session-access-types/`
**Prerequisites**: [plan.md](/home/marius/work/repos/escalade/specs/007-session-access-types/plan.md), [spec.md](/home/marius/work/repos/escalade/specs/007-session-access-types/spec.md), [research.md](/home/marius/work/repos/escalade/specs/007-session-access-types/research.md), [data-model.md](/home/marius/work/repos/escalade/specs/007-session-access-types/data-model.md), [openapi.yaml](/home/marius/work/repos/escalade/specs/007-session-access-types/contracts/openapi.yaml)

**Tests**: Aucune tache de test dediee n est incluse, car la specification ne demande pas explicitement une approche TDD. La verification independante de chaque story s appuie sur [quickstart.md](/home/marius/work/repos/escalade/specs/007-session-access-types/quickstart.md) et sur la suite pytest existante en validation finale.

**Organization**: Les taches sont groupees par user story pour permettre une livraison incrementale du MVP d inscription controlee, puis des droits referent/prof, puis du calendrier mixte complet.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut etre executee en parallele
- **[Story]**: User story concernee (`[US1]`, `[US2]`, `[US3]`)
- Chaque tache cite les fichiers exacts a modifier ou creer
- Les taches couvrent explicitement les controles d acces, l audit, la validation smartphone et la reprise manuelle admin

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparer les surfaces partagees du parcours prof et les primitives d affichage communes

- [X] T001 Creer le gabarit d edition prof dans `/home/marius/work/repos/escalade/src/templates/sessions/teacher_occurrence_form.html`
- [X] T002 [P] Ajouter les styles partages pour types de seance, etats d acces et actions prof dans `/home/marius/work/repos/escalade/src/static/css/app.css`
- [X] T003 [P] Etendre les widgets partages de selection de type et de prof dans `/home/marius/work/repos/escalade/src/sessions/forms.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Poser les primitives de donnees et de politique d acces qui bloquent toutes les stories

**CRITICAL**: Aucune user story ne commence avant la fin de cette phase

- [X] T004 Mettre a jour le schema des comptes pour le passport orange dans `/home/marius/work/repos/escalade/src/accounts/models.py` et `/home/marius/work/repos/escalade/src/accounts/migrations/`
- [X] T005 [P] Ajouter le type de seance, l affectation prof et les rattachements de cours dans `/home/marius/work/repos/escalade/src/sessions/models.py` et `/home/marius/work/repos/escalade/src/sessions/migrations/`
- [X] T006 Implementer les helpers derives de politique d acces et de motif de refus dans `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/bookings/services.py`
- [X] T007 [P] Etendre l enregistrement des evenements d audit pour passport, rattachement cours et edition prof dans `/home/marius/work/repos/escalade/src/audit/services.py` et `/home/marius/work/repos/escalade/src/audit/models.py`
- [X] T008 Adapter la synchronisation des creneaux et les gardes de responsabilite pour exclure les occurrences de cours dans `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/sessions/views_admin.py`
- [X] T009 Preparer les contextes admin partages pour choisir les cours, adherents et profs dans `/home/marius/work/repos/escalade/src/accounts/views_admin.py` et `/home/marius/work/repos/escalade/src/sessions/views_admin.py`

**Checkpoint**: Le schema, la politique d acces et les evenements d audit sont prets pour implementer les stories sans ambiguite metier

---

## Phase 3: User Story 1 - S inscrire seulement aux seances autorisees (Priority: P1) MVP

**Goal**: Permettre a l admin d attribuer les droits necessaires et a l adherent de ne voir `S inscrire` que sur les occurrences autorisees par son profil et leur type

**Independent Test**: Avec trois adherents tests ayant des droits differents, chacun ouvre une pratique libre et une occurrence de cours depuis le calendrier. Les actions disponibles changent correctement selon le passport orange, l accreditation referent/responsable et les rattachements a des cours, sans inscription automatique.

- [X] T010 [US1] Etendre la mise a jour des comptes pour gerer passport orange et rattachements de cours dans `/home/marius/work/repos/escalade/src/accounts/views_admin.py` et `/home/marius/work/repos/escalade/src/templates/admin/accounts/account_list.html`
- [X] T011 [P] [US1] Etendre les parcours admin de creation et d edition pour distinguer pratique libre et cours avec prof par defaut dans `/home/marius/work/repos/escalade/src/sessions/forms.py`, `/home/marius/work/repos/escalade/src/sessions/views_admin.py`, `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_list.html` et `/home/marius/work/repos/escalade/src/templates/admin/sessions/occurrence_form.html`
- [X] T012 [US1] Appliquer les regles d inscription par type de seance et profil utilisateur dans `/home/marius/work/repos/escalade/src/bookings/services.py`, `/home/marius/work/repos/escalade/src/bookings/views.py` et `/home/marius/work/repos/escalade/src/sessions/services.py`
- [X] T013 [P] [US1] Mettre a jour le calendrier membre pour exposer les CTA autorises, bloques et l inscription manuelle aux cours dans `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html`, `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html` et `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`
- [X] T014 [US1] Rendre visibles les indices de reprise manuelle pour droits retires et inscriptions incoherentes dans `/home/marius/work/repos/escalade/src/templates/admin/accounts/account_list.html`, `/home/marius/work/repos/escalade/src/templates/admin/bookings/session_reservations.html` et `/home/marius/work/repos/escalade/specs/007-session-access-types/quickstart.md`

**Checkpoint**: Le MVP bloque toutes les inscriptions non autorisees et permet les inscriptions legitimes depuis le calendrier sans automatisme de reservation

---

## Phase 4: User Story 2 - Operer selon le role referent ou prof (Priority: P2)

**Goal**: Permettre au referent de conserver la couverture des pratiques libres et au prof de modifier uniquement les occurrences de ses propres cours

**Independent Test**: Avec un utilisateur cumule referent et prof, un testeur verifie qu il peut couvrir une pratique libre, modifier une occurrence d un cours qui lui est attribue et qu il ne peut ni modifier un autre cours ni changer une serie complete.

- [X] T015 [US2] Restreindre les resumes de couverture et les actions sur creneaux aux seules pratiques libres dans `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html`
- [X] T016 [P] [US2] Construire le formulaire d edition occurrence-only pour prof dans `/home/marius/work/repos/escalade/src/sessions/forms.py` et `/home/marius/work/repos/escalade/src/templates/sessions/teacher_occurrence_form.html`
- [X] T017 [US2] Ajouter la route et la vue securisees d edition prof sur ses propres cours dans `/home/marius/work/repos/escalade/src/sessions/urls.py` et `/home/marius/work/repos/escalade/src/sessions/views.py`
- [X] T018 [US2] Exposer l affectation prof et les points d entree d edition prof sans ouvrir l administration globale dans `/home/marius/work/repos/escalade/src/templates/admin/sessions/occurrence_form.html`, `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_list.html`, `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html` et `/home/marius/work/repos/escalade/src/static/css/app.css`
- [X] T019 [US2] Enregistrer les editions prof et les indices de rollback admin dans `/home/marius/work/repos/escalade/src/sessions/services.py`, `/home/marius/work/repos/escalade/src/audit/services.py` et `/home/marius/work/repos/escalade/src/templates/admin/audit/session_history.html`

**Checkpoint**: Le referent et le prof disposent de leurs droits respectifs sans fuite vers l administration globale

---

## Phase 5: User Story 3 - Comprendre un calendrier mixte selon le type de seance (Priority: P3)

**Goal**: Garder un calendrier unique lisible qui distingue clairement pratiques libres et cours, y compris quand ils se chevauchent

**Independent Test**: Sur une semaine contenant une pratique libre et un cours simultanes, un testeur ouvre successivement les deux occurrences. Il voit bien deux elements distincts et un panneau de detail qui change selon le type sans melanger les regles metier.

- [X] T020 [US3] Etendre le view-model calendrier avec libelles de type, affichage prof et metadonnees de chevauchement mixte dans `/home/marius/work/repos/escalade/src/sessions/services.py`
- [X] T021 [P] [US3] Differencier les cartes et panneaux detail entre pratique libre et cours dans `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html`
- [X] T022 [P] [US3] Affiner la hierarchie mobile pour occurrences simultanees et etats sans prof dans `/home/marius/work/repos/escalade/src/static/css/app.css` et `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`
- [X] T023 [US3] Preserver des motifs de refus lisibles et la continuite de selection pendant la navigation hebdomadaire dans `/home/marius/work/repos/escalade/src/sessions/views.py`, `/home/marius/work/repos/escalade/src/bookings/views.py` et `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`

**Checkpoint**: Le calendrier mixte reste comprehensible meme avec des occurrences simultanees et des details conditionnels par type

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finaliser la documentation d exploitation, l alignement contrat et la coherence de vocabulaire

- [X] T024 [P] Mettre a jour la validation operationnelle et les consignes de reprise manuelle dans `/home/marius/work/repos/escalade/specs/007-session-access-types/quickstart.md` et `/home/marius/work/repos/escalade/specs/007-session-access-types/data-model.md`
- [X] T025 Revalider l alignement contrat-plan sur les endpoints de droits, d edition prof et de calendrier mixte dans `/home/marius/work/repos/escalade/specs/007-session-access-types/contracts/openapi.yaml` et `/home/marius/work/repos/escalade/specs/007-session-access-types/plan.md`
- [X] T026 [P] Harmoniser la terminologie et les badges sur les ecrans admin et membre dans `/home/marius/work/repos/escalade/src/templates/admin/accounts/account_list.html`, `/home/marius/work/repos/escalade/src/templates/admin/sessions/series_list.html`, `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html` et `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: aucune dependance, peut demarrer immediatement
- **Phase 2: Foundational**: depend de la phase 1 et bloque toutes les stories
- **Phase 3: US1**: depend de la phase 2
- **Phase 4: US2**: depend de la phase 2
- **Phase 5: US3**: depend de la phase 3 pour raffiner le calendrier mixte deja rendu actionnable
- **Phase 6: Polish**: depend des stories retenues pour la livraison

### User Story Dependencies

- **US1**: premier increment MVP, livre les droits d inscription et l administration minimale des acces
- **US2**: peut commencer apres la fondation et reste testable independamment via l edition prof et la couverture referent
- **US3**: depend du calendrier membre deja adapte par US1 pour affiner la cohabitation cours/pratique libre

### Within Each User Story

- Poser d abord les entrees admin et les gardes serveur
- Brancher ensuite les services metier et l audit
- Finaliser avec le rendu smartphone, les messages de refus et la reprise manuelle

### Suggested Completion Order

1. Phase 1
2. Phase 2
3. Phase 3 (US1) pour le MVP d inscription controlee
4. Phase 4 (US2) pour les droits referent/prof
5. Phase 5 (US3) pour la lisibilite du calendrier mixte
6. Phase 6

---

## Parallel Opportunities

- `T002` et `T003` peuvent avancer en parallele en phase 1
- `T005` et `T007` peuvent avancer en parallele une fois `T004` lancee
- Dans `US1`, `T011` et `T013` peuvent avancer en parallele apres la fondation
- Dans `US2`, `T016` peut avancer pendant que `T017` prepare la route et la vue
- Dans `US3`, `T021` et `T022` peuvent avancer en parallele apres `T020`
- En phase de polish, `T024` et `T026` peuvent avancer en parallele

---

## Parallel Example: User Story 1

```bash
Task: "Etendre les parcours admin de creation et d edition pour distinguer pratique libre et cours avec prof par defaut dans /home/marius/work/repos/escalade/src/sessions/forms.py, /home/marius/work/repos/escalade/src/sessions/views_admin.py, /home/marius/work/repos/escalade/src/templates/admin/sessions/series_list.html et /home/marius/work/repos/escalade/src/templates/admin/sessions/occurrence_form.html"
Task: "Mettre a jour le calendrier membre pour exposer les CTA autorises, bloques et l inscription manuelle aux cours dans /home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html, /home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html et /home/marius/work/repos/escalade/src/templates/sessions/session_list.html"
```

## Parallel Example: User Story 2

```bash
Task: "Construire le formulaire d edition occurrence-only pour prof dans /home/marius/work/repos/escalade/src/sessions/forms.py et /home/marius/work/repos/escalade/src/templates/sessions/teacher_occurrence_form.html"
Task: "Ajouter la route et la vue securisees d edition prof sur ses propres cours dans /home/marius/work/repos/escalade/src/sessions/urls.py et /home/marius/work/repos/escalade/src/sessions/views.py"
```

## Parallel Example: User Story 3

```bash
Task: "Differencier les cartes et panneaux detail entre pratique libre et cours dans /home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html et /home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html"
Task: "Affiner la hierarchie mobile pour occurrences simultanees et etats sans prof dans /home/marius/work/repos/escalade/src/static/css/app.css et /home/marius/work/repos/escalade/src/templates/sessions/session_list.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Terminer la phase 1
2. Terminer la phase 2
3. Livrer la phase 3 pour l inscription controlee par type et profil
4. Verifier sur smartphone les droits d inscription, les refus clairs et l absence d inscription automatique aux cours

### Incremental Delivery

1. Setup + Foundational
2. US1 pour les droits d inscription et l administration minimale
3. US2 pour les droits referent/prof et l edition occurrence-only
4. US3 pour la lisibilite du calendrier mixte
5. Polish pour documentation, vocabulaire et reprise manuelle

### Parallel Team Strategy

1. Toute l equipe ferme les phases 1 et 2
2. Puis:
   - Developpeur A: US1 et les surfaces membre/admin d acces
   - Developpeur B: US2 et le parcours prof
   - Developpeur C: US3 et la clarte du calendrier mixte
3. Integrer seulement apres verification que chaque story preserve audit, controles d acces et reprise manuelle

---

## Notes

- Toutes les taches respectent le format checklist `- [ ] T### ...`
- Les taches `US1`, `US2` et `US3` restent livrables par increments independants apres la phase fondation
- Le MVP recommande de s arreter apres `US1`
- La validation finale doit suivre [quickstart.md](/home/marius/work/repos/escalade/specs/007-session-access-types/quickstart.md)

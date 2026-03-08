# Tasks: Vue calendaire hebdomadaire des seances

**Input**: Design documents from `/home/marius/work/repos/escalade/specs/006-session-calendar/`
**Prerequisites**: [plan.md](/home/marius/work/repos/escalade/specs/006-session-calendar/plan.md), [spec.md](/home/marius/work/repos/escalade/specs/006-session-calendar/spec.md), [research.md](/home/marius/work/repos/escalade/specs/006-session-calendar/research.md), [data-model.md](/home/marius/work/repos/escalade/specs/006-session-calendar/data-model.md), [openapi.yaml](/home/marius/work/repos/escalade/specs/006-session-calendar/contracts/openapi.yaml)

**Tests**: Aucune tache de test dediee n est incluse, car la specification ne demande pas explicitement une approche TDD. La verification independante de chaque story s appuie sur [quickstart.md](/home/marius/work/repos/escalade/specs/006-session-calendar/quickstart.md) et sur la suite pytest existante en validation finale.

**Organization**: Les taches sont groupees par user story pour permettre une livraison incrementale du MVP mobile, puis du detail inline, puis des raffinements de lisibilite sur semaines chargees.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Peut etre executee en parallele
- **[Story]**: User story concernee (`[US1]`, `[US2]`, `[US3]`)
- Chaque tache cite les fichiers exacts a modifier ou creer
- Les taches couvrent explicitement la compatibilite metier existante, la validation smartphone, la reprise manuelle et la preservation du chemin d audit existant

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparer la surface de rendu commune du calendrier et figer les points d entree de la feature

- [X] T001 Creer les partials du calendrier hebdomadaire dans `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html`
- [X] T002 [P] Ajouter les ancres CSS partagees du calendrier hebdomadaire dans `/home/marius/work/repos/escalade/src/static/css/app.css`
- [X] T003 [P] Aligner le contrat et le scenario de validation du calendrier dans `/home/marius/work/repos/escalade/specs/006-session-calendar/contracts/openapi.yaml` et `/home/marius/work/repos/escalade/specs/006-session-calendar/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Poser les primitives communes de navigation semaine, de selection inline et de preservation du flux metier existant

**CRITICAL**: Aucune user story ne commence avant la fin de cette phase

- [X] T004 Implementer la normalisation de `week_start` et de `selected_occurrence` dans `/home/marius/work/repos/escalade/src/sessions/services.py`
- [X] T005 [P] Construire les view-models `CalendarWeek`, `CalendarDay` et `CalendarOccurrenceBlock` dans `/home/marius/work/repos/escalade/src/sessions/services.py`
- [X] T006 [P] Refondre l entree membre des seances pour consommer l etat de page hebdomadaire dans `/home/marius/work/repos/escalade/src/sessions/views.py`
- [X] T007 [P] Propager le contexte de retour `week_start` et `selected_occurrence` dans `/home/marius/work/repos/escalade/src/bookings/views.py` et `/home/marius/work/repos/escalade/src/sessions/views.py`
- [X] T008 [P] Conserver l acces direct a une seance comme point de compatibilite dans `/home/marius/work/repos/escalade/src/sessions/urls.py` et `/home/marius/work/repos/escalade/src/sessions/views.py`
- [X] T009 Preserver le chemin de services existant pour reservation, responsabilite et audit dans `/home/marius/work/repos/escalade/src/bookings/views.py`, `/home/marius/work/repos/escalade/src/sessions/views.py` et `/home/marius/work/repos/escalade/specs/006-session-calendar/quickstart.md`

**Checkpoint**: La page membre peut resoudre une semaine, une selection et un retour de contexte sans casser les regles metier ni l audit existants

---

## Phase 3: User Story 1 - Consulter la semaine en un coup d oeil sur smartphone (Priority: P1) MVP

**Goal**: Afficher les seances ouvertes dans une grille hebdomadaire `8h-23h` lisible sur smartphone, avec navigation de semaine et etats essentiels visibles sans ouvrir une fiche distincte

**Independent Test**: Sur smartphone, un adherent connecte ouvre `/sessions/`, voit la semaine courante dans une grille `8h-23h`, distingue les seances par jour et horaire, repere les etats essentiels et peut passer a la semaine precedente ou suivante sans quitter l ecran.

- [X] T010 [US1] Remplacer la liste lineaire des seances par la page calendrier hebdomadaire dans `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`
- [X] T011 [P] [US1] Rendre les colonnes de jours, l echelle horaire et les blocs condenses dans `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html` et `/home/marius/work/repos/escalade/src/static/css/app.css`
- [X] T012 [US1] Exposer les etats essentiels de chaque seance dans la grille via `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html`
- [X] T013 [P] [US1] Ajouter la navigation semaine precedente et suivante ainsi que l etat vide mobile dans `/home/marius/work/repos/escalade/src/sessions/views.py`, `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html` et `/home/marius/work/repos/escalade/src/static/css/app.css`

**Checkpoint**: Le parcours membre dispose d un MVP calendarise testable sans detail inline complet

---

## Phase 4: User Story 2 - Voir et utiliser les details sans changer de page (Priority: P2)

**Goal**: Afficher le detail complet de la seance selectionnee sous la grille et permettre reservation, desinscription et responsabilite depuis le meme ecran

**Independent Test**: Depuis `/sessions/`, un adherent selectionne une seance dans la grille, voit le detail se charger sous le calendrier, reserve ou annule depuis cette zone et reste sur la meme semaine avec la meme seance selectionnee. Un responsable accredite peut aussi y prendre ou quitter un creneau.

- [X] T014 [US2] Construire le `InlineOccurrenceDetail` et la selection de seance active dans `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/sessions/views.py`
- [X] T015 [P] [US2] Implementer le panneau detail inline avec actions scopees par role dans `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html` et `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`
- [X] T016 [US2] Rediriger reservation et desinscription vers le contexte de calendrier actif dans `/home/marius/work/repos/escalade/src/bookings/views.py` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html`
- [X] T017 [US2] Rediriger prise et abandon de responsabilite vers le contexte de calendrier actif dans `/home/marius/work/repos/escalade/src/sessions/views.py` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html`
- [X] T018 [P] [US2] Convertir la fiche detail historique en point de compatibilite et mettre a jour les liens membre dans `/home/marius/work/repos/escalade/src/sessions/views.py`, `/home/marius/work/repos/escalade/src/templates/sessions/session_detail.html` et `/home/marius/work/repos/escalade/src/templates/bookings/my_reservations.html`
- [X] T019 [P] [US2] Harmoniser les messages de retour et les CTA inline avec la charte existante dans `/home/marius/work/repos/escalade/src/static/css/app.css`, `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html`

**Checkpoint**: Le parcours membre principal devient un ecran unique calendrier + detail inline + actions existantes

---

## Phase 5: User Story 3 - Garder une interface sobre et lisible meme quand la semaine est chargee (Priority: P3)

**Goal**: Conserver une lecture claire en semaine dense grace a des libelles courts, un detail unique, des indicateurs hors plage et une hierarchie visuelle stable

**Independent Test**: Avec une semaine contenant plusieurs seances, des titres longs et des etats differents, la grille reste lisible sur smartphone, un seul detail est ouvert a la fois, les debordements `8h-23h` restent comprehensibles et l utilisateur n est pas noye dans le texte.

- [X] T020 [US3] Implementer les regles de raccourcissement de libelles et de condensation des blocs dans `/home/marius/work/repos/escalade/src/sessions/services.py` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html`
- [X] T021 [P] [US3] Ajouter les indicateurs de debordement horaire et de densite de grille dans `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html` et `/home/marius/work/repos/escalade/src/static/css/app.css`
- [X] T022 [US3] Garantir qu une seule seance detaillee reste active et que la reselection reste stable entre changements de semaine dans `/home/marius/work/repos/escalade/src/sessions/views.py` et `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`
- [X] T023 [P] [US3] Affiner la lisibilite mobile des semaines chargees, des badges et de la hierarchie inline dans `/home/marius/work/repos/escalade/src/static/css/app.css` et `/home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html`

**Checkpoint**: Le calendrier reste exploitable et sobre meme dans les cas limites de densite et de contenu long

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finaliser la documentation d usage, la reprise manuelle et le nettoyage des references obsoletes

- [X] T024 [P] Reconciler le contrat final et les etapes de validation mobile dans `/home/marius/work/repos/escalade/specs/006-session-calendar/contracts/openapi.yaml` et `/home/marius/work/repos/escalade/specs/006-session-calendar/quickstart.md`
- [X] T025 Valider la reprise manuelle admin, la minimisation des donnees et le repli de compatibilite dans `/home/marius/work/repos/escalade/specs/006-session-calendar/quickstart.md` et `/home/marius/work/repos/escalade/specs/006-session-calendar/data-model.md`
- [X] T026 [P] Nettoyer les libelles et references membre encore bases sur un changement de page dans `/home/marius/work/repos/escalade/src/templates/sessions/session_list.html`, `/home/marius/work/repos/escalade/src/templates/sessions/session_detail.html` et `/home/marius/work/repos/escalade/src/templates/bookings/my_reservations.html`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: aucune dependance, peut demarrer immediatement
- **Phase 2: Foundational**: depend de la phase 1 et bloque toutes les user stories
- **Phase 3: US1**: depend de la phase 2
- **Phase 4: US2**: depend de la phase 2 et reutilise la surface calendrier posee par US1
- **Phase 5: US3**: depend de la phase 3 et affine la densite du calendrier une fois la surface semaine stabilisee
- **Phase 6: Polish**: depend des stories retenues pour la livraison

### User Story Dependencies

- **US1**: premier increment MVP, livre la lecture hebdomadaire mobile
- **US2**: ajoute le detail inline et les actions sans casser le MVP de lecture
- **US3**: affine la lisibilite et les cas denses apres stabilisation de la vue semaine

### Within Each User Story

- Poser d abord les donnees de presentation ou l etat serveur
- Brancher ensuite templates, liens et CTA
- Finaliser avec messages, compatibilite, validation mobile et reprise manuelle

### Suggested Completion Order

1. Phase 1
2. Phase 2
3. Phase 3 (US1) pour le MVP mobile
4. Phase 4 (US2) pour le parcours mono-ecran complet
5. Phase 5 (US3) pour la lisibilite dense
6. Phase 6

---

## Parallel Opportunities

- `T002` et `T003` peuvent avancer en parallele pendant la phase 1
- `T005`, `T006`, `T007` et `T008` peuvent avancer en parallele apres `T004`
- Dans `US1`, `T011` et `T013` peuvent avancer en parallele apres `T010`
- Dans `US2`, `T015`, `T018` et `T019` peuvent avancer en parallele apres `T014`
- Dans `US3`, `T021` et `T023` peuvent avancer en parallele apres `T020`
- Dans `Polish`, `T024` et `T026` peuvent avancer en parallele

---

## Parallel Example: User Story 1

```bash
Task: "Rendre les colonnes de jours, l echelle horaire et les blocs condenses dans /home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html et /home/marius/work/repos/escalade/src/static/css/app.css"
Task: "Ajouter la navigation semaine precedente et suivante ainsi que l etat vide mobile dans /home/marius/work/repos/escalade/src/sessions/views.py, /home/marius/work/repos/escalade/src/templates/sessions/session_list.html et /home/marius/work/repos/escalade/src/static/css/app.css"
```

## Parallel Example: User Story 2

```bash
Task: "Implementer le panneau detail inline avec actions scopees par role dans /home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html et /home/marius/work/repos/escalade/src/templates/sessions/session_list.html"
Task: "Convertir la fiche detail historique en point de compatibilite et mettre a jour les liens membre dans /home/marius/work/repos/escalade/src/sessions/views.py, /home/marius/work/repos/escalade/src/templates/sessions/session_detail.html et /home/marius/work/repos/escalade/src/templates/bookings/my_reservations.html"
```

## Parallel Example: User Story 3

```bash
Task: "Ajouter les indicateurs de debordement horaire et de densite de grille dans /home/marius/work/repos/escalade/src/templates/sessions/_calendar_grid.html et /home/marius/work/repos/escalade/src/static/css/app.css"
Task: "Affiner la lisibilite mobile des semaines chargees, des badges et de la hierarchie inline dans /home/marius/work/repos/escalade/src/static/css/app.css et /home/marius/work/repos/escalade/src/templates/sessions/_calendar_detail.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Terminer la phase 1
2. Terminer la phase 2
3. Livrer la phase 3 pour la vue semaine `8h-23h`
4. Verifier la lecture mobile, les etats essentiels et la navigation de semaine

### Incremental Delivery

1. Setup + Foundational
2. US1 pour la grille hebdomadaire
3. US2 pour le detail inline et les actions mono-ecran
4. US3 pour les raffinements de lisibilite dense
5. Polish pour documentation et repli manuel

### Parallel Team Strategy

1. Toute l equipe ferme les phases 1 et 2
2. Puis:
   - Developpeur A: surface calendrier US1
   - Developpeur B: detail inline US2 apres stabilisation du view-model
   - Developpeur C: lisibilite dense US3 apres stabilisation de la grille

---

## Notes

- Toutes les taches respectent le format checklist `- [ ] T### ...`
- Les memoires `.specify/memory/product.md` et `.specify/memory/test-registry.md` sont absentes du repo au moment de la generation
- Les invariants metier viennent des specs `001-free-session-booking`, `003-club-visual-refresh` et `004-session-opener-management`
- Le MVP recommande de s arreter apres `US1` pour obtenir une premiere livraison demonstrable

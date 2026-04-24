# Implementation Plan: Vue calendaire hebdomadaire des seances

**Branch**: `006-session-calendar` | **Date**: 2026-03-08 | **Spec**: [spec.md](/home/marius/work/repos/escalade/specs/006-session-calendar/spec.md)
**Input**: Feature specification from `/specs/006-session-calendar/spec.md`

## Summary

Transformer le parcours membre des seances en une vue hebdomadaire mobile-first sur l application Django existante, en remplacant la liste lineaire et la fiche detail separee par une grille semaine `8h-23h` avec detail inline sous le calendrier. Le plan retenu conserve le monolithe a rendu serveur, reutilise les services de reservation, de responsabilite et d audit deja en place, et introduit seulement une couche de presentation et de navigation par parametres de requete pour limiter les changements de page.

## Technical Context

**Language/Version**: Python 3.12 dans le repo actuel, cible compatible Python 3.13  
**Primary Dependencies**: Django 5.2, templates Django server-side, authentification/session Django, feuille de style statique `src/static/css/app.css`  
**Storage**: SQLite applicatif existant; aucun changement de schema attendu pour cette feature  
**Testing**: pytest, pytest-django, tests d integration Django, test de contrat OpenAPI, revue manuelle mobile; Playwright existe dans le repo pour un complement eventuel  
**Target Platform**: navigateurs web mobile first, desktop en second  
**Project Type**: application web monolithique Django avec rendu serveur  
**Performance Goals**: lecture d une semaine et selection d une seance en moins de 30 secondes sur smartphone; affichage du detail inline et declenchement de l action principale en moins de 90 secondes  
**Constraints**: simplicite et lisibilite prioritaires, aucun changement des regles metier existantes, aucun cout recurrent supplementaire, audit conserve, details sous la grille plutot que sur une page separee, memoires `.specify/memory/product.md` et `.specify/memory/test-registry.md` absentes du repo  
**Scale/Scope**: un club unique, quelques seances par semaine, densite moderee du planning, parcours membre concentre sur une seule page hebdomadaire  
**Operational Recovery**: l admin doit pouvoir verifier ou corriger une situation depuis les ecrans d administration existants; un acces direct de compatibilite a une seance peut rester disponible comme repli si la navigation inline echoue  
**Cost Ceiling**: zero ou quasi zero cout recurrent, sans bibliotheque ou service externe obligatoire

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked and still passed after Phase 1 design.*

- **Mobile-first web**: PASS. Le parcours principal est la consultation puis l action depuis un smartphone dans une vue semaine.
- **Operational simplicity**: PASS. Le design conserve le rendu serveur Django et n ajoute aucune exploitation quotidienne nouvelle.
- **Cost control**: PASS. Aucun service tiers ni dependance payante n est introduit.
- **Roles and rules**: PASS. Les roles et permissions des specs 001 et 004 restent inchanges; seul le mode de presentation evolue.
- **Traceability**: PASS. Les actions inline reutilisent les services et traces d audit deja requis pour reservation, annulation et responsabilite.
- **MVP first**: PASS. Le MVP couvre d abord la vue semaine, la selection d une seance et les actions inline, avant toute finition optionnelle.
- **Data minimization**: PASS. Aucun nouveau type de donnee personnelle n est ajoute; les donnees affichees sont deja presentes dans le produit.
- **Manual recovery**: PASS. L administration existante reste la procedure de secours si un utilisateur ou un benevole doit verifier une situation manuellement.

## Project Structure

### Documentation (this feature)

```text
specs/006-session-calendar/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── accounts/
├── audit/
├── bookings/
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── config/
├── sessions/
│   ├── models.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── static/
│   └── css/
│       └── app.css
├── templates/
│   ├── bookings/
│   └── sessions/
└── manage.py

tests/
├── contract/
├── e2e/
├── integration/
└── unit/
```

**Structure Decision**: Conserver le monolithe Django existant. La feature se concentre sur `sessions/views.py`, `sessions/services.py`, `bookings/views.py`, `sessions/urls.py`, les templates `src/templates/sessions/` et la feuille `src/static/css/app.css`, sans split frontend/backend ni nouveau stockage.

## Phase 0: Research Output

- Les choix de navigation, de rendu et de compatibilite sont documentes dans [research.md](/home/marius/work/repos/escalade/specs/006-session-calendar/research.md).
- Aucun `NEEDS CLARIFICATION` bloquant ne reste apres recherche.
- `.specify/memory/product.md` et `.specify/memory/test-registry.md` sont absents du depot; la planification s appuie donc sur la constitution, la spec [001-free-session-booking/spec.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/spec.md), la spec [003-club-visual-refresh/spec.md](/home/marius/work/repos/escalade/specs/003-club-visual-refresh/spec.md) et la spec [004-session-opener-management/spec.md](/home/marius/work/repos/escalade/specs/004-session-opener-management/spec.md).
- La recherche confirme qu une vue semaine a rendu serveur avec selection inline et parametres de requete est plus simple et plus robuste qu un calendrier client riche.

## Phase 1: Design Output

- Le modele conceptuel de presentation et les entites existantes reutilisees sont documentes dans [data-model.md](/home/marius/work/repos/escalade/specs/006-session-calendar/data-model.md).
- Le contrat HTTP de reference pour la page calendrier hebdomadaire et les actions inline est defini dans [openapi.yaml](/home/marius/work/repos/escalade/specs/006-session-calendar/contracts/openapi.yaml).
- Le scenario de validation locale et mobile est documente dans [quickstart.md](/home/marius/work/repos/escalade/specs/006-session-calendar/quickstart.md).
- Le contexte agent sera resynchronise a partir de ce plan via `update-agent-context.sh`.

## Post-Design Constitution Check

- **Mobile-first web**: PASS. La page cible principale est la vue semaine membre sur petit ecran, avec detail et actions inline.
- **Operational simplicity**: PASS. Le plan reste dans les vues/templates existants et minimise les nouvelles surfaces de maintenance.
- **Cost control**: PASS. Aucun moteur de calendrier externe, abonnement ou service additionnel n est necessaire.
- **Roles and rules**: PASS. Le contrat conserve strictement les permissions et regles existantes; la compatibilite metier est explicite.
- **Traceability**: PASS. Les POST de reservation, annulation et responsabilite continuent de passer par les memes services audites.
- **MVP first**: PASS. Le plan cible d abord la consultation hebdomadaire et le detail unique sous la grille avant toute optimisation visuelle secondaire.
- **Data minimization**: PASS. Le modele ajoute uniquement des structures de presentation derivees en memoire.
- **Manual recovery**: PASS. Les ecrans admin existants et un acces de compatibilite a une seance fournissent un repli clair.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

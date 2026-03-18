# Implementation Plan: Types de seance et droits d acces

**Branch**: `007-session-access-types` | **Date**: 2026-03-18 | **Spec**: [spec.md](/home/marius/work/repos/escalade/specs/007-session-access-types/spec.md)
**Input**: Feature specification from `/specs/007-session-access-types/spec.md`

## Summary

Etendre le monolithe Django existant pour distinguer les pratiques libres des cours, appliquer des droits d inscription explicites selon le profil utilisateur et permettre a un prof de modifier uniquement les occurrences de ses propres cours. Le plan retenu reutilise le calendrier hebdomadaire de la feature 006, ajoute un schema minimal pour le passport orange, les rattachements aux cours et l affectation prof, puis centralise les controles d acces dans les services existants de seances, reservations et audit.

## Technical Context

**Language/Version**: Python 3.12 dans le repo actuel, cible compatible Python 3.13  
**Primary Dependencies**: Django 5.2, templates Django server-side, authentification/session Django, applications `accounts`, `sessions`, `bookings`, `audit`, feuille de style `src/static/css/app.css`  
**Storage**: SQLite applicatif existant avec migrations de schema sur `accounts` et `sessions`; les reservations et audits restent dans la base locale existante  
**Testing**: pytest, pytest-django, tests unitaires, integration Django, contrats OpenAPI, verification manuelle mobile sur la vue calendrier et les parcours admin/prof  
**Target Platform**: navigateurs web mobile first, desktop en second  
**Project Type**: application web monolithique Django avec rendu serveur  
**Performance Goals**: un adherent eligibile atteint le detail d une occurrence et s y inscrit en moins de 90 secondes sur smartphone; un prof modifie une occurrence de son cours en moins de 2 minutes; le calendrier mixte reste lisible meme avec des occurrences simultanees  
**Constraints**: budget quasi nul, aucune inscription automatique aux cours, admin seul pour l administration globale, edition prof limitee aux occurrences de ses propres cours, couverture referent reservee aux pratiques libres, conservation de l audit existant, reprise manuelle possible par l admin  
**Scale/Scope**: un club unique, quelques pratiques libres et cours par semaine, quelques dizaines d adherents actifs, quelques profs/referents, calendrier hebdomadaire unique partage par tous les membres connectes  
**Operational Recovery**: l administrateur doit pouvoir corriger manuellement les droits utilisateur, les inscriptions et les occurrences depuis les ecrans web d administration existants ou etendus; le parcours membre conserve une redirection stable vers le calendrier apres toute action  
**Cost Ceiling**: zero ou quasi zero cout recurrent, sans service externe ni dependance payante obligatoire

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked and still passed after Phase 1 design.*

- **Mobile-first web**: PASS. Le parcours principal reste le calendrier membre sur smartphone, avec detail adapte au type de seance.
- **Operational simplicity**: PASS. Le plan reste dans le monolithe Django et ajoute des droits explicites plutot qu une nouvelle application ou un outil externe.
- **Cost control**: PASS. Aucun service payant ou bibliotheque externe obligatoire n est introduit.
- **Roles and rules**: PASS. Les roles visibles, permissions et regles tranchees sont explicites; aucun point metier critique ne reste implicite.
- **Traceability**: PASS. Les changements de droits, les inscriptions, desinscriptions, couvertures referent et editions d occurrences restent traces.
- **MVP first**: PASS. Le MVP couvre d abord les droits d inscription, le calendrier mixte et l edition occurrence-only par le prof avant toute automatisation secondaire.
- **Data minimization**: PASS. Seules les donnees necessaires a l eligibilite, a l affichage du type de seance et aux droits d edition sont ajoutees.
- **Manual recovery**: PASS. L administrateur conserve des ecrans de correction pour les droits, affectations et inscriptions.

## Project Structure

### Documentation (this feature)

```text
specs/007-session-access-types/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- openapi.yaml
`-- tasks.md
```

### Source Code (repository root)

```text
src/
|-- accounts/
|   |-- models.py
|   |-- urls_admin.py
|   `-- views_admin.py
|-- audit/
|   |-- models.py
|   `-- services.py
|-- bookings/
|   |-- models.py
|   |-- services.py
|   |-- urls.py
|   `-- views.py
|-- config/
|   `-- urls.py
|-- sessions/
|   |-- forms.py
|   |-- models.py
|   |-- services.py
|   |-- urls.py
|   |-- urls_admin.py
|   |-- views.py
|   `-- views_admin.py
|-- static/
|   `-- css/
|       `-- app.css
|-- templates/
|   |-- admin/
|   |   |-- accounts/
|   |   `-- sessions/
|   `-- sessions/
`-- manage.py

tests/
|-- contract/
|-- e2e/
|-- integration/
`-- unit/
```

**Structure Decision**: Conserver le monolithe Django existant. Les changements se concentrent sur `accounts` pour les droits explicites, `sessions` pour les types de seance, les occurrences et les vues admin/prof, `bookings` pour les controles d inscription, `audit` pour les nouveaux evenements traces, et les templates serveur pour adapter le calendrier et les formulaires.

## Phase 0: Research Output

- Les choix structurants sont documentes dans [research.md](/home/marius/work/repos/escalade/specs/007-session-access-types/research.md).
- Aucun point bloquant ne reste apres recherche.
- La recherche confirme que le plus petit changement coherent est d etendre `SessionSeries` et `SessionOccurrence` avec un type explicite, puis d ajouter des relations de droit plutot que de multiplier les roles globaux.
- Le plan retient une route d edition prof dediee aux occurrences de cours pour eviter de reexposer l administration globale.

## Phase 1: Design Output

- Le modele conceptuel des nouvelles entites et validations est documente dans [data-model.md](/home/marius/work/repos/escalade/specs/007-session-access-types/data-model.md).
- Le contrat HTTP de reference pour le calendrier mixte, l administration des droits et l edition prof est defini dans [openapi.yaml](/home/marius/work/repos/escalade/specs/007-session-access-types/contracts/openapi.yaml).
- Le scenario de verification locale du MVP est documente dans [quickstart.md](/home/marius/work/repos/escalade/specs/007-session-access-types/quickstart.md).
- Le contexte agent doit etre resynchronise apres ce plan via `update-agent-context.sh`.

## Post-Design Constitution Check

- **Mobile-first web**: PASS. Le calendrier mixte reste l entree principale et les actions d inscription restent disponibles sur smartphone.
- **Operational simplicity**: PASS. Le modele ajoute des droits explicites mais garde les ecrans et services Django existants comme base.
- **Cost control**: PASS. Les droits, cours et editions prof sont geres sans nouveau service recurrent.
- **Roles and rules**: PASS. Les controles d acces sont centralises autour du type de seance, du passport orange, des rattachements de cours et de l affectation prof.
- **Traceability**: PASS. Le plan etend seulement les types d audit deja en place.
- **MVP first**: PASS. Les ecrans et verifications couvrent d abord les flux critiques d inscription et d edition occurrence-only.
- **Data minimization**: PASS. Les nouveaux champs et relations sont limites aux besoins d eligibilite et d affichage du prof.
- **Manual recovery**: PASS. L admin peut corriger les droits et les inscriptions sans traitement opaque.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

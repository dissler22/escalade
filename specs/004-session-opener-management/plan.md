# Implementation Plan: Gestion des responsables de pratique libre

**Branch**: `004-session-opener-management` | **Date**: 2026-03-08 | **Spec**: [spec.md](/home/marius/work/repos/escalade/specs/004-session-opener-management/spec.md)
**Input**: Feature specification from `/specs/004-session-opener-management/spec.md`

## Summary

Introduire la gestion des `responsables` sur les pratiques libres en conservant l application web Django existante et les regles de reservation de la spec 001. Le plan technique retenu ajoute une accreditation responsable distincte du role admin, transforme la seance reservable actuelle en seance parent portant des creneaux reservables enfants de 90 minutes maximum, reutilise l audit existant pour tracer responsabilites et annulations, puis ajoute un traitement planifie simple sur la VM pour les relances J-7 et les annulations J-2 avec envoi depuis une adresse email configuree hors code.

## Technical Context

**Language/Version**: Python 3.12 dans le repo actuel, cible compatible Python 3.13  
**Primary Dependencies**: Django 5.2, Gunicorn, templates Django server-side, authentification/session Django  
**Storage**: SQLite applicatif existant + fichiers statiques locaux + configuration email en variables d environnement  
**Testing**: pytest, pytest-django, tests de contrat OpenAPI bases sur fichiers, tests integration Django existants  
**Target Platform**: navigateurs web mobile first, desktop admin en second  
**Project Type**: application web monolithique Django avec rendu serveur  
**Performance Goals**: prise de responsabilite en moins d une minute sur smartphone, creation admin ou correction simple en moins de deux minutes, traitements J-7 et J-2 executes sur la meme journee sans intervention humaine  
**Constraints**: budget quasi nul, administration simple, reprise manuelle obligatoire, aucune lecture automatique des emails entrants, compatibilite avec les specs 001 et 002, memoires `.specify/memory/product.md` et `.specify/memory/test-registry.md` absentes du repo  
**Scale/Scope**: un club unique, volume benevole modere, quelques seances hebdomadaires, faible concurrence simultanee hors prises de dernieres places et de dernier responsable  
**Operational Recovery**: l admin doit pouvoir accrediter, affecter, retirer, annuler et prevenir manuellement sans dependre des automatismes email ou du traitement planifie  
**Cost Ceiling**: aucun abonnement obligatoire supplementaire; reutilisation de la VM existante et d une boite email dediee du club

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked and still passed after Phase 1 design.*

- Mobile-first web: PASS. Le parcours critique reste la prise de responsabilite et la consultation des creneaux sur smartphone, sans app native.
- Operational simplicity: PASS. Le fonctionnement nominal repose sur des ecrans admin simples et un traitement planifie leger; la reprise manuelle reste documentee.
- Cost control: PASS. Aucun service payant nouveau n est requis au-dela de la VM existante et d une boite email deja acceptee.
- Roles and rules: PASS. Les roles `adherent`, `responsable accredite` et `administrateur` sont explicites, ainsi que les regles `J-7`, `J-2`, `1 responsable exact` et `90 minutes max`.
- Traceability: PASS. Les affectations responsable, retraits, annulations de creneaux, rappels et corrections manuelles sont toutes tracees.
- MVP first: PASS. Le socle manuel admin + responsable est defini avant l automatisation email planifiee.
- Data minimization: PASS. La feature ajoute seulement l accreditation responsable, l affectation de responsable, les creneaux, et l adresse email d envoi visible.
- Manual recovery: PASS. L admin peut couvrir ou annuler un creneau et relancer les inscrits manuellement si l automatisation echoue.

## Project Structure

### Documentation (this feature)

```text
specs/004-session-opener-management/
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
│   ├── models.py
│   ├── views_admin.py
│   └── urls_admin.py
├── audit/
│   ├── models.py
│   ├── services.py
│   └── views.py
├── bookings/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── views_admin.py
├── config/
│   ├── env.py
│   ├── settings.py
│   └── urls.py
├── sessions/
│   ├── models.py
│   ├── services.py
│   ├── forms.py
│   ├── views.py
│   ├── views_admin.py
│   └── urls_admin.py
├── templates/
│   ├── sessions/
│   ├── bookings/
│   └── accounts/
└── static/css/app.css

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Conserver le monolithe Django existant. La logique responsable se greffe principalement dans `accounts`, `sessions`, `bookings`, `audit` et `config`, sans split frontend/backend ni service annexe.

## Phase 0 Research Scope

- Valider la meilleure representation du role `responsable` sans casser les permissions existantes.
- Choisir comment faire evoluer `SessionOccurrence` pour porter une seance parent et des creneaux reservables.
- Choisir le mecanisme le plus simple pour l automation `J-7` et `J-2` sur la VM de la spec 002.
- Encadrer l integration email sortante avec adresse visible pour l admin et secret hors interface.
- Identifier l impact minimal sur l audit existant pour couvrir responsabilites et annulations de creneaux.

## Phase 1 Design Scope

- Ajouter le modele parent/enfant pour seance et creneau sans perdre les reservations existantes.
- Etendre le modele utilisateur avec l accreditation responsable, sans transformer `responsable` en role admin.
- Definir les formulaires, vues et routes member/admin pour couverture responsable et correction manuelle.
- Definir le contrat HTTP de reference pour les flux adherent, responsable et admin.
- Prevoir la configuration email et l execution planifiee compatibles avec la VM simple de la spec 002.

## Complexity Tracking

Aucune derogation a la constitution n est necessaire pour cette feature.

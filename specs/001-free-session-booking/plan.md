# Implementation Plan: Reservations de seances libres

**Branch**: `001-free-session-booking` | **Date**: 2026-03-07 | **Spec**: [spec.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/spec.md)
**Input**: Feature specification from `/specs/001-free-session-booking/spec.md`

## Summary

Livrer une web app mobile-first permettant a des adherents autorises de reserver ou annuler une place sur une seance libre, et a des administrateurs de creer, modifier, ouvrir, fermer et corriger manuellement des seances ponctuelles ou regulieres. Le plan retient une application web monolithique server-side, peu couteuse, avec authentification par compte, capacites definies manuellement, audit systematique et reprise manuelle pour tous les flux critiques.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: Django 5.x, Django authentication/session framework, PostgreSQL driver  
**Storage**: SQLite pour developpement local, PostgreSQL pour environnement partage ou production  
**Testing**: Pytest pour logique metier et integration, Playwright pour parcours smartphone critiques  
**Target Platform**: Navigateurs web mobiles modernes en priorite, navigateurs desktop en second  
**Project Type**: Web app mobile-first monolithique avec rendu serveur  
**Performance Goals**: Parcours connexion + reservation en moins de 2 minutes sur smartphone, affichage des listes de seances en moins de 2 secondes dans le contexte d'un club unique  
**Constraints**: Budget quasi nul, operations admin simples, aucune automatisation avancee obligatoire, traces d'audit obligatoires, reprise manuelle obligatoire  
**Scale/Scope**: Un club, quelques dizaines a quelques centaines de comptes, quelques dizaines de seances par semaine au maximum, usage benevole  
**Operational Recovery**: Les administrateurs doivent pouvoir corriger manuellement les seances, reservations, ouvertures/fermetures et comptes sans intervention technique  
**Cost Ceiling**: Hebergement et exploitation a cout nul ou quasi nul, sans dependance payante obligatoire

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Mobile-first web**: PASS. Le parcours principal est un flux smartphone navigateur pour consulter les seances, reserver et annuler. Aucun besoin natif n'est introduit.
- **Operational simplicity**: PASS. L'administration garde la main sur la capacite, l'ouverture et les corrections. Aucun traitement automatique complexe n'est requis pour operer.
- **Cost control**: PASS. Le plan retient une pile standard deployable a cout quasi nul, sans service tiers payant indispensable.
- **Roles and rules**: PASS. Deux roles explicites seulement: adherent autorise et administrateur. Les regles de capacite, ouverture et absence de liste d'attente sont tranchees.
- **Traceability**: PASS. Toute creation/modification de seance, reservation, annulation et correction manuelle reste historisee.
- **MVP first**: PASS. Le MVP couvre creation de seance, reservation, annulation et correction manuelle avant tout automatisme avance.
- **Data minimization**: PASS. Les donnees retenues sont limitees au compte, a la reservation, a la seance et a l'audit.
- **Manual recovery**: PASS. Chaque flux critique a une contrepartie manuelle cote admin.

## Project Structure

### Documentation (this feature)

```text
specs/001-free-session-booking/
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
├── config/
├── accounts/
├── sessions/
├── bookings/
├── audit/
├── templates/
└── static/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Le depot ne contient pas encore d'application. Le plan retient un projet web monolithique unique dans `src/` afin de limiter la complexite, de mutualiser auth/admin/rendu HTML, et de rester aligne avec l'objectif de simplicite operationnelle.

## Phase 0: Research Output

- Les choix techniques structurants sont documentes dans [research.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/research.md).
- Aucun `NEEDS CLARIFICATION` bloquant ne reste apres recherche.
- `product.md` et `test-registry.md` etaient absents du depot; le plan s'appuie donc sur la spec de feature et la constitution comme sources normatives.
- Aucun autre `specs/*/spec.md` existant n'impose de contrainte supplementaire sur cette feature.

## Phase 1: Design Output

- Le modele de donnees cible est documente dans [data-model.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/data-model.md).
- Les contrats applicatifs sont definis dans [openapi.yaml](/home/marius/work/repos/escalade/specs/001-free-session-booking/contracts/openapi.yaml).
- Le scenario de validation locale et de demonstration est decrit dans [quickstart.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/quickstart.md).
- Le contexte agent sera synchronise a partir de ce plan une fois les fichiers ecrits.

## Post-Design Constitution Check

- **Mobile-first web**: PASS. Les contrats et flux privilegient les ecrans mobiles et le rendu web.
- **Operational simplicity**: PASS. La conception reste manuelle pour l'ouverture, la capacite et les corrections.
- **Cost control**: PASS. Aucun composant de design n'introduit de service externe payant obligatoire.
- **Roles and rules**: PASS. Les endpoints et entites respectent strictement les deux roles definis.
- **Traceability**: PASS. Le modele inclut un journal d'audit consultable par seance.
- **MVP first**: PASS. Aucun mecanisme de liste d'attente, notifications ou synchronisation externe n'est introduit.
- **Data minimization**: PASS. Le modele conserve uniquement les donnees utiles a l'acces, a l'inscription et a la reprise d'incident.
- **Manual recovery**: PASS. Les contrats admin couvrent les corrections manuelles et la desactivation de comptes.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

# Implementation Plan: Rafraichissement visuel USMV

**Branch**: `003-club-visual-refresh` | **Date**: 2026-03-08 | **Spec**: [spec.md](/home/marius/work/repos/escalade/specs/003-club-visual-refresh/spec.md)
**Input**: Feature specification from `/specs/003-club-visual-refresh/spec.md`

## Summary

Renforcer l'identite visuelle de l'application Django existante en alignant ses ecrans adherent et admin sur les marqueurs du site public USMV Escalade, tout en conservant le monolithe a rendu serveur, les parcours mobiles existants et l'ensemble des regles metier, permissions et traces d'audit deja definis par la spec 001.

## Technical Context

**Language/Version**: Python 3.12+ dans le repo actuel  
**Primary Dependencies**: Django 5.x, templates Django server-side, feuille de style statique unique, authentification/session Django  
**Storage**: SQLite applicatif existant, sans changement de schema requis pour cette feature  
**Testing**: Pytest existant pour integration et logique metier, revue visuelle manuelle sur smartphone et desktop, controle contractuel sur le contrat OpenAPI  
**Target Platform**: Navigateurs web mobiles modernes en priorite, navigateurs desktop en second  
**Project Type**: Monolithe Django mobile-first a rendu serveur  
**Performance Goals**: Ecran de connexion et parcours liste/detail/reservation restent utilisables en moins de 2 minutes sur smartphone; les reperes visuels principaux doivent etre identifiables en moins de 5 secondes selon la spec  
**Constraints**: Aucune modification de fonctionnalite metier, aucune nouvelle dependance payante obligatoire, aucun nouveau type de donnee personnelle, coherence entre ecrans adherent et admin, fonctionnement degrade acceptable si un actif visuel manque  
**Scale/Scope**: Un club, quelques dizaines a quelques centaines de comptes, une seule application web, un jeu limite de templates HTML et une feuille CSS centrale  
**Operational Recovery**: Retour possible a une presentation plus simple ecran par ecran si une evolution visuelle masque une action, sans interrompre les parcours existants  
**Cost Ceiling**: Cout recurrent nul ou quasi nul, sans service externe requis pour la presentation visuelle

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Mobile-first web**: PASS. Le coeur du travail vise les ecrans smartphone existants avant les variantes desktop, sans besoin natif.
- **Operational simplicity**: PASS. Le plan conserve un monolithe simple, une feuille de style centrale et une revue visuelle manuelle exploitable par l'equipe.
- **Cost control**: PASS. Aucun service tiers payant ni infrastructure supplementaire n'est introduit.
- **Roles and rules**: PASS. Les roles `adherent` et `administrateur` restent inchanges; la refonte ne modifie ni permissions ni regles metier.
- **Traceability**: PASS. Aucun nouvel evenement d'audit n'est requis, et l'habillage ne doit pas degrader la lisibilite des traces existantes.
- **MVP first**: PASS. Le MVP couvre d'abord les ecrans coeur et les composants partages avant toute finition decorative optionnelle.
- **Data minimization**: PASS. Aucun nouveau champ personnel n'est ajoute; seuls des actifs visuels publics et des regles de presentation sont concerns.
- **Manual recovery**: PASS. Un retour a un habillage plus sobre reste possible si un ecran rafraichi compromet la comprehension.

## Project Structure

### Documentation (this feature)

```text
specs/003-club-visual-refresh/
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
├── manage.py
├── config/
├── accounts/
├── sessions/
├── bookings/
├── audit/
├── templates/
│   ├── accounts/
│   ├── sessions/
│   ├── bookings/
│   └── admin/
└── static/
    └── css/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Conserver le monolithe Django existant et concentrer la feature dans les templates HTML partages, les vues deja en place et `src/static/css/app.css`. Aucun split frontend/backend, aucun nouveau service UI et aucun changement de structure de donnees n'est necessaire.

## Phase 0: Research Output

- Les choix de refonte visuelle et de portee technique sont documentes dans [research.md](/home/marius/work/repos/escalade/specs/003-club-visual-refresh/research.md).
- Aucun `NEEDS CLARIFICATION` bloquant ne reste apres recherche.
- `.specify/memory/product.md` et `.specify/memory/test-registry.md` sont absents du depot; la planification s'appuie donc sur la constitution, la spec [003-club-visual-refresh/spec.md](/home/marius/work/repos/escalade/specs/003-club-visual-refresh/spec.md) et la spec metier [001-free-session-booking/spec.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/spec.md).
- La recherche confirme que le meilleur levier est un systeme visuel leger partage entre pages HTML existantes plutot qu'une reprise complete du theme public du site.

## Phase 1: Design Output

- Le modele conceptuel de presentation est documente dans [data-model.md](/home/marius/work/repos/escalade/specs/003-club-visual-refresh/data-model.md).
- Le contrat HTTP des ecrans et assets a verifier pendant la refonte est defini dans [openapi.yaml](/home/marius/work/repos/escalade/specs/003-club-visual-refresh/contracts/openapi.yaml).
- Le scenario de validation locale et de revue visuelle est documente dans [quickstart.md](/home/marius/work/repos/escalade/specs/003-club-visual-refresh/quickstart.md).
- Le contexte agent sera resynchronise a partir de ce plan via `update-agent-context.sh`.

## Post-Design Constitution Check

- **Mobile-first web**: PASS. Le design cible d'abord la connexion, la liste des seances, le detail et les ecrans admin sur petit ecran.
- **Operational simplicity**: PASS. Le plan repose sur une structure CSS partagee et des composants reutilisables dans les templates existants.
- **Cost control**: PASS. Aucun composant de design n'impose un abonnement, une librairie payante ou un service externe obligatoire.
- **Roles and rules**: PASS. Les contrats et entites de design n'ajoutent aucun role ni comportement metier.
- **Traceability**: PASS. Les pages d'audit et les messages de statut restent dans le perimetre de la charte visuelle.
- **MVP first**: PASS. Le plan couvre d'abord le shell global, les messages, les boutons, les cartes, les formulaires et les tableaux des ecrans actifs.
- **Data minimization**: PASS. Le modele de donnees de design ne requiert aucun stockage personnel additionnel.
- **Manual recovery**: PASS. La quickstart et la recherche prevoient une validation ecran par ecran et la possibilite de repli visuel.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

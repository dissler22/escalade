# Implementation Plan: Deploiement VM simple

**Branch**: `002-gcp-vm-deploy` | **Date**: 2026-03-07 | **Spec**: [spec.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/spec.md)
**Input**: Feature specification from `/specs/002-gcp-vm-deploy/spec.md`

## Summary

Adapter le monolithe Django existant pour une mise en production simple sur une VM Google Cloud unique en conservant un cout minimal: reverse proxy frontal, serveur WSGI dedie, base SQLite persistante sur la meme machine, configuration externalisee, procedure de release manuelle, smoke test public et rollback documente.

## Technical Context

**Language/Version**: Python 3.12+ dans le repo actuel, cible normalisee sur Python 3.13 pour la VM  
**Primary Dependencies**: Django 5.x, Gunicorn, Nginx, systemd, SQLite standard library support  
**Storage**: SQLite sur repertoire persistant partage de la VM + sauvegardes horodatees sur la meme machine  
**Testing**: Pytest existant, smoke test HTTP manuel sur pages HTML existantes, verification de restart service apres reboot  
**Target Platform**: Navigateurs web mobiles modernes pour les adherents; VM Linux unique pour l'hebergement  
**Project Type**: Monolithe Django a rendu serveur  
**Performance Goals**: Page de connexion et liste des seances accessibles en moins de 2 minutes depuis smartphone; release standard completee en moins de 15 minutes; rollback en moins de 20 minutes  
**Constraints**: VM unique `instance-20260307-190711`, IP publique initiale `34.71.54.146`, budget quasi nul, base sur la meme machine, pas de service managé obligatoire, release et rollback manuels, secrets hors repo  
**Scale/Scope**: Un club, quelques dizaines a quelques centaines de comptes, faible concurrence simultanee, un seul environnement de production  
**Operational Recovery**: Sauvegarde pre-release, retour a la release precedente, restauration du fichier SQLite coherent, verification manuelle du parcours connexion puis liste des seances  
**Cost Ceiling**: Aucun cout recurrent supplementaire obligatoire au-dela de la VM existante et d'un stockage local ou de sauvegarde basique

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Mobile-first web**: PASS. Le parcours de verification prioritaire reste l'ouverture depuis smartphone de la page de connexion puis de la liste des seances existante.
- **Operational simplicity**: PASS. Le plan retient une pile standard avec peu de composants, une release manuelle courte et une reprise documentee.
- **Cost control**: PASS. Le deploiement reste sur la VM existante, sans base managée, sans service tiers payant et sans automatisation lourde.
- **Roles and rules**: PASS. Les roles `adherent`, `administrateur club` et `mainteneur` sont explicites; le mainteneur seul gere la machine et le rollback.
- **Traceability**: PASS. Le plan ajoute une trace operationnelle de sauvegarde, release, verification et rollback, sans remettre en cause l'audit metier existant.
- **MVP first**: PASS. Le MVP livre d'abord une mise en ligne stable, une release manuelle et un rollback avant toute sophistication d'observabilite.
- **Data minimization**: PASS. Les nouvelles donnees portent uniquement sur la configuration d'execution, les sauvegardes et les traces operationnelles necessaires.
- **Manual recovery**: PASS. Le fallback est explicite: remise en service de la release precedente puis restauration du fichier de donnees si necessaire.

## Project Structure

### Documentation (this feature)

```text
specs/002-gcp-vm-deploy/
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
└── static/

tests/
├── contract/
├── integration/
└── unit/

docs/
└── deployment.md
```

**Structure Decision**: Conserver le monolithe Django existant dans `src/`, concentrer les adaptations de production dans la configuration Django, la documentation de deploiement et de futurs artefacts d'exploitation legerement couples au repo. Aucun split frontend/backend n'est introduit.

## Phase 0: Research Output

- Les choix structurants de deploiement et d'exploitation sont documentes dans [research.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/research.md).
- Aucun `NEEDS CLARIFICATION` ne reste dans le contexte technique apres recherche.
- `.specify/memory/product.md` et `.specify/memory/test-registry.md` etaient absents du depot; la planification s'appuie donc sur la constitution, la spec `002-gcp-vm-deploy` et la spec metier [001-free-session-booking/spec.md](/home/marius/work/repos/escalade/specs/001-free-session-booking/spec.md).
- La spec metier existante impose de preserver le parcours mobile connexion -> liste des seances -> reservation ainsi que l'audit metier deja present.

## Phase 1: Design Output

- Le modele de donnees operationnel est documente dans [data-model.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/data-model.md).
- Le contrat HTTP minimal de publication et de smoke test est documente dans [openapi.yaml](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/contracts/openapi.yaml).
- La procedure de validation et de repetition du deploiement est documentee dans [quickstart.md](/home/marius/work/repos/escalade/specs/002-gcp-vm-deploy/quickstart.md).
- Le contexte agent sera resynchronise a partir de ce plan via le script `update-agent-context.sh`.

## Post-Design Constitution Check

- **Mobile-first web**: PASS. Les controles publics portent sur les ecrans HTML existants utilises depuis smartphone.
- **Operational simplicity**: PASS. Le design retient un layout `releases/current/shared`, des services standards et un rollback par bascule simple.
- **Cost control**: PASS. Aucun composant de design n'impose un abonnement externe ou une seconde machine.
- **Roles and rules**: PASS. Les responsabilites machine restent bornees au mainteneur; les admins fonctionnels continuent d'utiliser seulement l'application.
- **Traceability**: PASS. Les releases, sauvegardes et rollbacks laissent une trace exploitable en complement de l'audit metier.
- **MVP first**: PASS. Le plan ne depend pas d'une CI/CD, d'un monitoring avance ou d'une base externe pour la premiere mise en ligne.
- **Data minimization**: PASS. Les nouveaux artefacts de donnees se limitent a la config runtime, aux releases et aux sauvegardes.
- **Manual recovery**: PASS. La restauration des donnees et la remise en ligne precedente sont detaillees et testables.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

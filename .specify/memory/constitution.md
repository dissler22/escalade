<!--
Sync Impact Report
- Version change: unversioned template -> 1.0.0
- Modified principles:
  - PRINCIPLE_1_NAME -> I. Simplicite operationnelle
  - PRINCIPLE_2_NAME -> II. Mobile-first web, pas natif par defaut
  - PRINCIPLE_3_NAME -> III. Cout nul ou quasi nul
  - PRINCIPLE_4_NAME -> IV. Roles et regles explicites
  - PRINCIPLE_5_NAME -> V. Tracabilite des inscriptions et annulations
  - Added VI. Priorite au MVP avant les automatismes avances
  - Added VII. Donnees minimales et confidentialite pragmatique
  - Added VIII. Administration simple avec reprise manuelle possible
- Added sections:
  - Product Boundaries
  - Delivery Workflow
- Removed sections:
  - None
- Templates requiring updates:
  - updated .specify/templates/plan-template.md
  - updated .specify/templates/spec-template.md
  - updated .specify/templates/tasks-template.md
  - updated .specify/templates/commands/README.md (placeholder file to keep the directory present)
- Follow-up TODOs:
  - None
-->
# escalade Constitution

## Core Principles

### I. Simplicite operationnelle
Le produit MUST rester exploitable par une association benevole sans intervention
technique quotidienne. Toute fonctionnalite nouvelle MUST reduire ou maintenir la
charge operationnelle courante. Si une fonctionnalite ajoute une tache recurrente,
la spec MUST decrire le declencheur, le role responsable, la duree cible et la
procedure de secours. Rationale: le turnover benevole impose un systeme simple,
comprenable et peu fragile.

### II. Mobile-first web, pas natif par defaut
Le parcours principal MUST etre concu d'abord pour un smartphone via navigateur
web. Toute spec MUST decrire le parcours critique sur petit ecran tactile avant
les variantes desktop. Une application native MUST NOT etre introduite par
defaut; elle n'est autorisee que si une spec demontre qu'une exigence precise ne
peut pas etre satisfaite par la web app et qu'une comparaison de cout et de
maintenance a ete approuvee. Rationale: l'usage principal vise le telephone,
sans alourdir l'exploitation ni la maintenance.

### III. Cout nul ou quasi nul
L'architecture, l'hebergement et les dependances externes MUST privilegier des
solutions a cout nul ou quasi nul. Toute dependance payante ou toute hausse de
cout recurrent MUST etre justifiee par ecrit avec plafond de cout, solution de
sortie et approbation de gouvernance avant implementation. Une fonctionnalite qui
suppose un abonnement externe pour son fonctionnement nominal MUST NOT etre le
choix par defaut. Rationale: le projet doit rester soutenable pour une
association a budget contraint.

### IV. Roles et regles explicites
Chaque spec MUST identifier les roles concernes, leurs permissions et les regles
metier tranchees par la fonctionnalite. Toute permission non documentee MUST etre
consideree interdite. Toute regle metier encore ouverte MUST etre laissee dans la
spec comme point a arbitrer; elle MUST NOT etre inventee dans le code, les tests
ou l'interface. Rationale: la clarte des droits et des regles evite les decisions
implicites difficiles a corriger ensuite.

### V. Tracabilite des inscriptions et annulations
Toute creation, modification ou annulation d'inscription ayant un effet sur une
seance MUST produire une trace horodatee avec l'action, le role acteur,
l'entite concernee et, si disponible, le motif. Cette trace MUST rester
consultable par l'administration et MUST NOT etre effacee par une mise a jour de
l'etat courant. Toute correction manuelle MUST laisser la meme trace. Rationale:
le club doit pouvoir expliquer une situation, resoudre un litige et reprendre un
incident sans ambiguite.

### VI. Priorite au MVP avant les automatismes avances
Les specs, plans et taches MUST isoler un MVP livrant le parcours coeur
inscription/annulation avant tout automatisme avance. Notifications, relances,
optimisations, synchronisations et autres automatismes MUST venir apres une
procedure manuelle exploitable, sauf si l'absence d'automatisation cree un risque
operationnel majeur documente. Rationale: la valeur initiale reside dans un flux
fiable et simple, pas dans l'automatisation prematuree.

### VII. Donnees minimales et confidentialite pragmatique
Le produit MUST collecter et conserver uniquement les donnees necessaires a
l'inscription, a l'administration de la seance et a la resolution d'incidents.
Chaque spec MUST enumerer les donnees creees ou exposees, leur finalite, les
roles qui y accedent et la regle de retention ou de suppression retenue. Les
donnees sensibles ou sans utilite operationnelle explicite MUST NOT etre ajoutees
par defaut. Rationale: limiter les donnees reduit le risque, la complexite et la
charge administrative.

### VIII. Administration simple avec reprise manuelle possible
Toute capacite d'administration MUST etre realisable depuis des ecrans web simples
et disposer d'une procedure de reprise manuelle quand un automatisme echoue ou
reste indisponible. Aucune fonctionnalite critique MUST dependre exclusivement
d'un traitement opaque sans possibilite de verification et de correction par un
responsable autorise. Rationale: l'association doit pouvoir continuer a operer,
meme en mode degrade.

## Product Boundaries

La constitution fixe des principes stables de produit et de realisation pour une
application web mobile-first de gestion des inscriptions aux seances de pratique
libre d'un club d'escalade benevole.

Elle ne tranche pas les regles metier encore mouvantes, notamment les quotas,
priorites de reservation, listes d'attente, regles d'eligibilite, penalites de
no-show, politiques de remboursement ou workflows de communication. Ces sujets
MUST etre definis dans les futures specs lorsqu'ils deviennent necessaires.

Toute spec MUST expliciter ce qui est tranche, ce qui ne l'est pas encore et le
comportement temporaire retenu pour le MVP. Aucun comportement implicite ne peut
servir de substitut a une regle metier non decidee.

## Delivery Workflow

Toute fonctionnalite MUST passer par une spec, un plan et une liste de taches
alignes sur cette constitution.

La spec MUST decrire au minimum le parcours smartphone principal, les roles et
permissions, les donnees manipulees, les evenements de trace generes, la
procedure de reprise manuelle et les points de regle metier encore ouverts.

Le plan MUST confirmer le respect du mobile-first web, du budget quasi nul, de la
simplicite operationnelle et du decoupage MVP avant automatisation. Toute
exception MUST etre documentee dans la section de suivi de complexite avant debut
d'implementation.

La liste de taches MUST inclure, quand le perimetre les touche, les travaux de
trace d'audit, les controles d'acces par role, la validation sur smartphone et la
procedure ou documentation de reprise manuelle. Une tache d'automatisation
avancee MUST NOT preceder la livraison du parcours manuel equivalent.

## Governance

Cette constitution prevaut sur les habitudes locales, templates et instructions
non versionnees du repo en cas de conflit.

La gouvernance du produit repose sur deux responsabilites explicites: un
responsable produit mandatant les besoins de l'association et un mainteneur du
repo validant la faisabilite technique. Une modification de constitution MUST
etre approuvee par ces deux responsabilites avant fusion. Si une meme personne
porte les deux responsabilites, la decision MUST etre tracee explicitement dans la
PR, le commit ou le journal de modification associe.

Toute proposition d'amendement MUST inclure: le diff de la constitution, le type
exact d'increment de version semantique, les impacts sur les templates et, si
necessaire, le plan de migration des specs ou travaux en cours.

La politique de versionnement semantique est normative:
- MAJOR pour toute suppression ou redefinition incompatible d'un principe ou d'une
  regle de gouvernance.
- MINOR pour tout ajout de principe, nouvelle section normative ou extension
  materielle des obligations.
- PATCH pour toute clarification, reformulation ou correction sans changement
  normatif.

Chaque plan de fonctionnalite et chaque revue de changement MUST verifier la
conformite a cette constitution. Toute derogation MUST etre documentee avec sa
justification, sa duree maximale et le responsable de sa resolution avant merge.

**Version**: 1.0.0 | **Ratified**: 2026-03-07 | **Last Amended**: 2026-03-07

# Feature Specification: Deploiement VM simple

**Feature Branch**: `002-gcp-vm-deploy`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: User description: "Prépare une spec 2 pour adapter cette app Django à un déploiement sur ma VM Google Cloud `instance-20260307-190711` (`us-central1- f`, IP publique `34.71.54.146`). Cible : `Django + Gunicorn + Nginx` sur la VM, base sur la même machine, approche simple et peu coûteuse. Analyse le repo, liste les adaptations minimales, propose la spec, la checklist de déploiement, les risques et le rollback. Ne modifie pas le repo avant validation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ouvrir l'application depuis le telephone apres mise en ligne (Priority: P1)

Un adherent ouvre l'adresse publique de l'application depuis son smartphone, arrive sur l'ecran de connexion, se connecte, consulte les seances et peut continuer le parcours de reservation existant sans connaitre l'infrastructure sous-jacente.

**Why this priority**: La valeur du deploiement est nulle si le parcours mobile deja specifie n'est pas accessible de facon fiable depuis l'exterieur.

**Independent Test**: Depuis un reseau exterieur a la VM, un testeur ouvre l'URL publique sur smartphone, se connecte avec un compte valide, atteint la liste des seances et confirme que l'application sert correctement les pages et feuilles de style.

**Acceptance Scenarios**:

1. **Given** l'application a ete deployee sur la VM et les services sont demarres, **When** un adherent ouvre l'adresse publique depuis son telephone, **Then** il atteint une page de connexion exploitable sans erreur serveur.
2. **Given** l'application est en ligne et les donnees existantes sont presentes, **When** un adherent se connecte puis ouvre la liste des seances, **Then** il retrouve les seances et reservations deja connues sans perte de donnees ni comportement degrade.

---

### User Story 2 - Mettre en ligne la premiere version sur une VM unique (Priority: P2)

Un mainteneur prepare une VM unique peu couteuse, y installe le service web, la publication publique et la base locale, puis suit une procedure documentee pour mettre l'application en ligne sans intervention manuelle dans le code.

**Why this priority**: Ce flux rend la mise en service repetable par une petite equipe benevole et limite le risque de derive operationnelle.

**Independent Test**: A partir d'une VM vierge du meme type, un mainteneur suit uniquement la checklist de deploiement, configure l'environnement d'execution, lance l'application et verifie qu'elle survit a un redemarrage machine.

**Acceptance Scenarios**:

1. **Given** une VM cible disponible et un acces administrateur a la machine, **When** le mainteneur suit la procedure d'installation initiale, **Then** l'application devient accessible publiquement et demarre automatiquement apres un reboot de la VM.
2. **Given** la configuration d'execution a ete preparee hors du depot, **When** le mainteneur deploie une nouvelle copie du code, **Then** les secrets, les hotes autorises et l'emplacement des donnees persistent sans reedition manuelle du code source.

---

### User Story 3 - Publier une mise a jour avec repli rapide (Priority: P3)

Un mainteneur prepare une sauvegarde, publie une nouvelle version, verifie rapidement le parcours critique, puis revient a la version precedente si la verification echoue ou si une migration degrade l'application.

**Why this priority**: Un hebergement sur VM unique reste un point de fragilite. Le repli rapide est indispensable pour proteger les reservations et limiter l'indisponibilite.

**Independent Test**: Sur un environnement de validation ou lors d'un exercice de repetition, le mainteneur cree une sauvegarde, simule une mise a jour en echec, restaure la version precedente, redemarre les services et confirme que l'application redevient utilisable.

**Acceptance Scenarios**:

1. **Given** une nouvelle version est prete a etre publiee, **When** le mainteneur execute la procedure de release, **Then** une sauvegarde horodatee est creee avant de basculer le trafic sur la nouvelle version.
2. **Given** la verification post-deploiement echoue, **When** le mainteneur declenche le rollback documente, **Then** la version precedente et les donnees coherentes sont restaurees dans le delai prevu.

### Edge Cases

- La VM redemarre seule apres maintenance ou incident d'infrastructure.
- Une mise a jour du code reussit mais les fichiers statiques publies ne correspondent pas a la version servie.
- Une migration de schema echoue en cours de release et laisse l'application indisponible.
- Le stockage local atteint sa limite et empeche l'ecriture de la base ou des sauvegardes.
- Deux operations d'administration modifient les reservations presque en meme temps sur une base locale unique.
- L'application n'a encore qu'une IP publique et aucun nom de domaine au moment de la validation initiale.
- Un role non autorise tente d'acceder aux ecrans ou fichiers d'administration de la machine.

## Requirements *(mandatory)*

### Roles & Rules

- **Actor Roles**:
  - `Adherent`: accede a l'application en lecture et action via le navigateur mobile une fois le service publie.
  - `Administrateur club`: exploite les ecrans d'administration fonctionnelle apres mise en ligne.
  - `Mainteneur / deployeur`: prepare la VM, configure l'execution, publie les versions, gere les sauvegardes et declenche le rollback si necessaire.
- **Explicit Permissions**:
  - Un adherent peut uniquement utiliser l'application publiee et ne dispose d'aucun acces machine.
  - Un administrateur club peut gerer les donnees applicatives via les ecrans prevus, mais ne modifie pas la configuration systeme de la VM.
  - Un mainteneur peut modifier la configuration d'execution, lancer une release, redemarrer les services et restaurer une sauvegarde.
  - Toute action non explicitement autorisee par cette spec est interdite.
- **Resolved Business Rules**:
  - Le perimetre cible un seul environnement de production sur une VM unique deja existante.
  - La publication publique doit utiliser la VM `instance-20260307-190711` et son IP `34.71.54.146` comme point d'entree initial.
  - Le deploiement doit rester compatible avec une approche simple et peu couteuse, sans service tiers payant indispensable.
  - La base principale, les sauvegardes et la configuration d'execution restent sur la meme machine mais hors de l'arborescence de code versionnee.
  - Les mises en production sont manuelles, encadrees par une sauvegarde prealable et une verification post-deploiement.
  - L'ouverture large aux adherents suppose un acces public protegeant les identifiants; si seule l'IP est disponible au depart, elle sert d'abord a la validation operateur avant ouverture generale.
  - Les architectures multi-VM, l'auto-scaling, les workers asynchrones et les services externes de base de donnees restent hors perimetre de cette spec.
- **Open Business Rules**:
  - Aucun point bloquant ouvert pour cette iteration.

### Functional Requirements

- **FR-001**: Le systeme MUST permettre de definir hors du code source la cle secrete, le mode debug, les hotes publics autorises et l'emplacement de la base locale.
- **FR-002**: Le systeme MUST pouvoir demarrer comme un service long vivant qui se relance automatiquement apres un redemarrage de la VM.
- **FR-003**: Le systeme MUST exposer un seul point d'entree web public sur la VM et MUST eviter l'exposition directe du processus applicatif au reseau public.
- **FR-004**: Le systeme MUST servir correctement les fichiers statiques apres chaque deploiement sans intervention manuelle dans le code.
- **FR-005**: Le systeme MUST conserver la base applicative, l'historique d'audit et les sauvegardes dans des emplacements persistants qui survivent aux redemarrages et aux mises a jour du code.
- **FR-006**: Le systeme MUST fournir une procedure documentee pour l'installation initiale sur une VM vierge du meme type que la cible.
- **FR-007**: Le systeme MUST fournir une procedure documentee pour les releases suivantes, incluant sauvegarde, mise a jour, verification et fermeture propre de la fenetre de maintenance.
- **FR-008**: Le systeme MUST appliquer les changements de schema et de fichiers statiques dans un ordre documente qui minimise le risque d'incoherence visible par les utilisateurs.
- **FR-009**: Le systeme MUST permettre a un mainteneur de revenir a la version precedente avec restauration des donnees coherentes si la release en cours echoue.
- **FR-010**: Le systeme MUST documenter les prerequis machine minimaux, les ports exposes, les repertoires persistants et le role responsable de chaque etape de deploiement.
- **FR-011**: Le systeme MUST rester exploitable dans le budget de la VM existante, sans abonnement supplementaire obligatoire pour le fonctionnement nominal.
- **FR-012**: Le systeme MUST proposer un controle de verification simple que l'administrateur ou le mainteneur peut executer apres deploiement pour confirmer la disponibilite du parcours connexion puis liste des seances.
- **FR-013**: Le systeme MUST consigner les evenements operationnels de release, de sauvegarde et de rollback dans un journal ou une trace consultable par le mainteneur.

### Minimal Adaptations to Current Application

- **Configuration**: Les reglages actuellement codes en dur pour le developpement doivent etre externalises afin de distinguer un usage local d'un usage VM public.
- **Persistance**: La base locale actuelle doit etre deplacee vers un emplacement persistant dedie a la production pour ne pas dependre du dossier de travail du depot.
- **Publication des assets**: Le projet doit preparer explicitement les fichiers statiques pour un service web frontal au lieu de compter sur le comportement du serveur de developpement.
- **Execution durable**: L'application doit disposer d'un mode de lancement adapte a un service permanent, pas uniquement a un serveur de developpement.
- **Documentation operatoire**: Le repo doit decrire l'installation initiale, la release, la sauvegarde, la verification et le rollback de facon executable par un mainteneur.
- **Durcissement minimal**: L'acces public doit cesser de reposer sur des reglages de developpement permissifs et sur une cle secrete de test.

### Audit & Operations

- **Audit Events**:
  - creation d'une sauvegarde avant release
  - debut d'une release
  - application des changements de schema
  - publication des fichiers statiques
  - redemarrage des services
  - verification post-deploiement
  - rollback declenche
  - restauration de donnees
- **Operational Procedure**:
  - Le mainteneur prepare d'abord une sauvegarde horodatee et confirme l'espace disque disponible.
  - Il publie ensuite la nouvelle version, applique les changements de schema et met a jour les fichiers publics necessaires.
  - Il redemarre les services permanents, verifie la page de connexion puis le parcours jusqu'a la liste des seances.
  - Si la verification est concluante, il clot la fenetre de maintenance et conserve la trace de release.
- **Manual Recovery**:
  - Si la nouvelle version ne demarre pas ou renvoie des erreurs, le mainteneur remet en service la version precedente sans attendre de correctif a chaud.
  - Si une migration ou un echec d'ecriture a rendu les donnees incoherentes, le mainteneur restaure la sauvegarde pre-release puis redemarre les services.
  - Si la machine reste accessible mais que l'ouverture generale n'est pas assez sure, l'acces est reserve au mainteneur pour validation jusqu'a mise en securite adequate.
- **Cost Impact**:
  - Aucun cout recurrent obligatoire n'est ajoute hors cout de la VM existante, de son stockage local et d'un eventuel stockage de sauvegarde basique a tres faible cout.

### Data & Privacy

- **Collected Data**:
  - secrets d'execution
  - liste des hotes publics autorises
  - base applicative de production
  - sauvegardes horodatees
  - traces de release et de rollback
  - journaux techniques minimaux de disponibilite
- **Purpose of Each Data Item**:
  - les secrets et hotes autorises servent a securiser l'acces public
  - la base de production sert a conserver comptes, seances, reservations et audit metier
  - les sauvegardes servent a restaurer un etat coherent
  - les traces de release et journaux servent a diagnostiquer un incident ou prouver qu'un rollback a ete execute
- **Access Scope**:
  - seuls les mainteneurs autorises accedent aux secrets, sauvegardes et journaux machine
  - les administrateurs club accedent aux donnees fonctionnelles via l'application, sans acces direct aux secrets ni aux fichiers systeme
  - les adherents n'accedent qu'aux donnees exposees par l'application selon la spec metier existante
- **Retention / Deletion Approach**:
  - les secrets actifs sont conserves tant que l'environnement existe puis supprimes lors de son decommissionnement
  - au minimum plusieurs sauvegardes recentes sont conservees pour couvrir un rollback et une reprise apres incident
  - les journaux techniques et traces de release sont conserves assez longtemps pour diagnostiquer un incident recent puis purges periodiquement

### Key Entities *(include if feature involves data)*

- **Environnement de production**: represente la VM cible, son point d'entree public, ses repertoires persistants et ses services permanents.
- **Configuration d'execution**: represente l'ensemble des valeurs sensibles ou variables necessaires pour lancer l'application sans modifier le code source.
- **Sauvegarde pre-release**: represente une copie horodatee des donnees et informations utiles a une restauration.
- **Version de release**: represente une revision publiable du code accompagnee de son etat de verification, de ses traces operationnelles et de son eventuel rollback.

### Assumptions

- La VM `instance-20260307-190711` est accessible en administration et dispose d'un stockage suffisant pour l'application, la base locale et plusieurs sauvegardes recentes.
- Le volume attendu reste celui d'un club unique avec peu d'utilisateurs simultanes, ce qui permet une base locale simple sur la meme machine pour le MVP.
- Aucun upload media utilisateur ni traitement asynchrone n'est requis pour cette iteration.
- Le premier acces public peut commencer par une validation limitee sur l'IP fournie avant ouverture plus large lorsque les conditions de securisation sont reunies.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Depuis un smartphone externe au reseau de la VM, 95 % des essais guides atteignent la page de connexion publique puis la liste des seances en moins de 2 minutes apres mise en ligne.
- **SC-002**: Un mainteneur peut realiser l'installation initiale sur une VM vierge comparable en moins de 90 minutes en suivant uniquement la documentation de deploiement.
- **SC-003**: Une release courante incluant sauvegarde, mise a jour et verification peut etre executee en moins de 15 minutes hors duree exceptionnelle de migration.
- **SC-004**: En cas d'echec post-release, un rollback vers la version precedente et un etat de donnees coherent peuvent etre completes en moins de 20 minutes.
- **SC-005**: Le fonctionnement nominal ne requiert aucun service payant supplementaire au-dela de la VM existante et d'un stockage local ou de sauvegarde basique compatible avec un budget associatif tres contraint.

## Deployment Checklist

1. Verifier l'acces administrateur a la VM cible, l'espace disque libre et la disponibilite du point d'entree public.
2. Installer les prerequis systeme et creer les repertoires persistants dedies a la configuration, aux donnees et aux sauvegardes.
3. Declarer la configuration d'execution de production hors du depot.
4. Installer l'application et ses dependances dans un environnement d'execution dedie.
5. Initialiser ou restaurer la base locale de production dans son emplacement persistant.
6. Publier les fichiers statiques, demarrer les services permanents et verifier leur redemarrage automatique.
7. Realiser le smoke test connexion puis liste des seances depuis un navigateur externe.
8. Documenter la version active, la date de mise en ligne et l'emplacement de la sauvegarde de reference.

## Risks

- L'absence initiale de point d'entree public suffisamment securise peut retarder l'ouverture aux adherents.
- Une base locale sur VM unique simplifie le cout mais augmente le risque de contention d'ecriture, de corruption locale ou de perte si la sauvegarde est insuffisante.
- La VM unique reste un point de panne unique pour l'application, la base et les sauvegardes locales.
- Une release manuelle mal sequencee peut provoquer une indisponibilite courte ou un decalage entre code, schema et assets.
- Des secrets laisses dans le code ou un mode debug actif exposeraient directement l'application a un risque evitable.

## Rollback Strategy

- Conserver la version precedente de l'application et au moins une sauvegarde pre-release identifiee avant chaque mise en production.
- Si la verification post-deploiement echoue, arreter la diffusion de la nouvelle version, remettre la version precedente, puis redemarrer les services permanents.
- Si les donnees ont ete modifiees de facon non exploitable pendant la release, restaurer la sauvegarde pre-release avant de rouvrir l'acces general.
- Apres rollback, verifier la connexion, la liste des seances, l'administration et l'historique recent avant de declarer l'incident clos.

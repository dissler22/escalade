# Research - Deploiement VM simple

## Decision 1: Garder un monolithe Django derriere un reverse proxy frontal

**Decision**: Deployer l'application existante comme un monolithe Django servi par Gunicorn derriere Nginx, avec supervision par systemd sur la VM unique.

**Rationale**: Le depot contient deja un point d'entree WSGI, une app a rendu serveur et aucune separation frontend/backend. Cette pile est standard, peu couteuse, facile a exploiter manuellement et compatible avec une VM unique.

**Alternatives considered**:

- Utiliser le serveur de developpement Django en production: trop fragile et non adapte a un service permanent public.
- Introduire des conteneurs des le MVP: faisable, mais ajoute une couche d'exploitation et de rollback non necessaire pour cette premiere mise en ligne.
- Heberger l'app derriere un service PaaS tiers: plus simple a court terme, mais contraire a la cible explicite de deploiement sur la VM existante.

## Decision 2: Conserver SQLite pour le MVP de production sur la meme machine

**Decision**: Garder SQLite pour la premiere production, en deplacant le fichier de base dans un repertoire persistant partage de la VM et en encadrant les releases par des sauvegardes horodatees.

**Rationale**: La charge attendue reste faible, le projet a deja SQLite en local, et la spec demande une approche simple et peu couteuse avec base sur la meme machine. Le risque principal est la concurrence d'ecriture; il reste acceptable pour un club unique si les sauvegardes et le rollback sont disciplines.

**Alternatives considered**:

- Passer immediatement a PostgreSQL local sur la meme VM: plus robuste en concurrence, mais ajoute administration, supervision et maintenance systeme.
- Base managée externe: meilleure isolation, mais depasse le besoin MVP et introduit un cout ou une dependance supplementaire.

## Decision 3: Externaliser toute la configuration de production hors du depot

**Decision**: Lire les secrets, hotes autorises, chemins persistants et mode debug depuis un fichier d'environnement ou des variables machine, conserves hors de l'arborescence versionnee.

**Rationale**: Le code actuel contient une cle secrete de test, `DEBUG = True` et `ALLOWED_HOSTS = ["*"]`. Ces valeurs doivent devenir specifiques a l'environnement sans forcer une edition manuelle du code a chaque release.

**Alternatives considered**:

- Garder des valeurs de production dans le repo: simple a court terme, mais risque de fuite et de divergence.
- Introduire un gestionnaire de secrets externe: plus propre, mais surdimensionne pour une VM unique et un budget contraint.

## Decision 4: Servir les fichiers statiques via le frontal web

**Decision**: Publier les assets statiques dans un repertoire dedie partage et les servir directement depuis Nginx.

**Rationale**: L'application utilise deja des templates HTML et un fichier CSS statique. Le frontal web sert les fichiers statiques plus efficacement et de maniere plus previsible qu'un service applicatif, tout en evitant une dependance additionnelle.

**Alternatives considered**:

- Servir les statics uniquement via l'application: plus simple en apparence, mais moins robuste et moins clair pour un deploiement public.
- Introduire WhiteNoise des le MVP: acceptable, mais moins naturel lorsque Nginx est deja le frontal choisi.

## Decision 5: Adopter un layout `releases/current/shared` pour faciliter le rollback

**Decision**: Organiser les deployments avec des releases horodatees, un lien `current` vers la version active et un repertoire `shared` pour la base, les statics publies, la configuration et les sauvegardes.

**Rationale**: Cette structure reste simple a comprendre, facilite le repli vers la release precedente et evite que la base ou les fichiers statiques dependent du dossier git actif.

**Alternatives considered**:

- Faire un `git pull` en place dans le dossier de travail: plus court a lancer, mais rollback plus incertain et couplage fort entre code, base et artefacts.
- Copier chaque nouvelle version par-dessus la precedente: rend difficile la comparaison, le rollback et le nettoyage.

## Decision 6: Utiliser les routes HTML existantes pour le smoke test de production

**Decision**: Le controle de disponibilite initial s'appuie sur les ecrans deja presents: `/`, `/login/`, `/sessions/`, `/bookings/mine/` et le CSS principal.

**Rationale**: Le besoin prioritaire est de verifier que le parcours réel connexion puis liste des seances fonctionne. Reutiliser les routes existantes evite d'ajouter un endpoint de sante juste pour le MVP de deploiement.

**Alternatives considered**:

- Ajouter un endpoint technique dedie de type `/healthz`: utile plus tard, mais non indispensable pour la premiere iteration.
- Se contenter d'un test de port ouvert: insuffisant pour prouver que l'application et les assets sont exploitables.

## Decision 7: Journaliser les operations de release au niveau systeme et dans un fichier simple

**Decision**: Conserver la trace des deployments, redemarrages et rollbacks via les journaux systeme et un journal d'exploitation horodate dans le repertoire partage.

**Rationale**: La spec impose une trace operationnelle consultable par le mainteneur. Les journaux systeme existent deja sur la machine et un fichier complementaire simple suffit pour reconstituer la chronologie d'une release.

**Alternatives considered**:

- Creer un modele Django specifique pour les releases: possible, mais ajoute des migrations et couple l'historique deploiement a l'application elle-meme.
- Ne garder aucune trace hors shell history: trop fragile pour une exploitation benevole.

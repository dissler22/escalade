# Research - Reservations de seances libres

## Decision 1: Utiliser une web app monolithique avec rendu serveur

**Decision**: Construire la V1 comme une seule application web mobile-first avec rendu serveur et interface d'administration integree.

**Rationale**: Le depot est vide, le besoin est simple, et le projet doit rester exploitable par des benevoles. Une architecture monolithique reduit le nombre de composants, facilite l'authentification, simplifie l'administration et permet de livrer plus vite le flux coeur.

**Alternatives considered**:

- SPA frontend + API separee: plus flexible, mais plus couteuse a monter et a maintenir pour une V1.
- Application mobile native: non conforme au principe mobile-first web par defaut, surdimensionnee pour le besoin.

## Decision 2: Authentification par comptes pre-provisionnes

**Decision**: L'acces repose sur des comptes nominatif pre-crees ou administres par le club, sans self-signup en V1.

**Rationale**: Le besoin utilisateur indique que les adresses email et mots de passe temporaires existent deja pour les personnes autorisees. Cela supprime une couche de validation supplementaire et garde le controle d'acces entierement cote administration.

**Alternatives considered**:

- Inscription libre avec validation ulterieure: ajoute un workflow d'approbation inutile en V1.
- Federation externe: introduit une dependance et une complexite non necessaires.

## Decision 3: Modeliser les seances en deux niveaux, serie hebdomadaire et occurrence

**Decision**: Separer les creneaux reguliers hebdomadaires des occurrences datees reservables.

**Rationale**: La spec demande a la fois de creer/modifier un schema recurrent et de surcharger une seule semaine. Deux niveaux de donnees rendent cette regle simple, explicite et testable.

**Alternatives considered**:

- Dupliquer manuellement chaque seance sans notion de serie: trop fastidieux pour l'administration.
- Mettre toute la logique dans une recurrence opaque: rendrait les exceptions d'une semaine plus fragiles.

## Decision 4: Pas d'automatisation avancee en V1

**Decision**: Ne pas introduire de liste d'attente, de notifications automatiques ou de logique d'ouverture conditionnelle.

**Rationale**: La spec tranche clairement ces points. Le MVP doit rester fiable et comprehensible avant toute sophistication.

**Alternatives considered**:

- Liste d'attente automatique: hors perimetre.
- Regles automatiques d'ouverture selon contexte: contraire au besoin explicite de garder la main cote admin.

## Decision 5: Audit synchrone des actions operationnelles

**Decision**: Journaliser immediatement les actions critiques de seance, de reservation et de correction admin au moment ou elles sont effectuees.

**Rationale**: La constitution impose une tracabilite consultable et non effacable par simple mise a jour d'etat. Une ecriture synchrone au fil de l'eau est plus simple a raisonner et a reprendre qu'un traitement asynchrone.

**Alternatives considered**:

- Journal d'audit asynchrone ou derive des logs techniques: trop fragile et moins fiable pour la reprise manuelle.
- Historique limite aux changements de reservation seulement: insuffisant car la creation/fermeture de seances doit aussi etre explicable.

## Decision 6: Choisir une base relationnelle simple avec strategie locale vs partagee

**Decision**: Utiliser SQLite pour le developpement local et une base relationnelle partagee type PostgreSQL pour un environnement heberge.

**Rationale**: Le projet a besoin de relations claires entre comptes, seances, reservations et audit. SQLite garde un demarrage leger. PostgreSQL reste un choix standard si le projet est heberge a plusieurs utilisateurs.

**Alternatives considered**:

- Fichiers plats ou tableur: trop fragile pour gerer la concurrence sur les dernieres places et l'audit.
- PostgreSQL uniquement des le premier jour: acceptable, mais moins leger pour prototyper dans un depot vide.

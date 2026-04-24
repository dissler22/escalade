# Spécification fonctionnelle du site à recréer

## Objet

Ce document décrit le site tel qu’il doit fonctionner, indépendamment de Django, des features historiques ou de l’implémentation actuelle.

Il sert de base pour reconstruire le produit from scratch, par exemple avec un frontend React, sans perdre les règles métier utiles.

Le contenu ci-dessous est déduit du comportement réel du dépôt:

- modèles, services, vues et templates dans `src/`
- tests unitaires et d’intégration dans `tests/`

## Finalité du produit

Le site permet à la section escalade de l’USM Viroflay de gérer:

- les inscriptions aux séances
- la distinction entre `pratique libre` et `cours`
- la couverture des créneaux de pratique libre par un référent
- la gestion des droits d’accès selon le profil
- les corrections manuelles par l’administration
- la traçabilité des actions importantes

Le parcours principal est mobile-first.

## Principes produit

1. Le point d’entrée membre est un calendrier hebdomadaire unique.
2. L’utilisateur agit depuis une seule page principale, sans navigation détaillée complexe.
3. Une séance peut être de type `pratique libre` ou `cours`.
4. La logique métier dépend fortement du type de séance.
5. La réservation d’un pratiquant porte sur une occurrence entière, pas sur un créneau.
6. La couverture par référent porte sur un créneau, pas sur l’occurrence entière.
7. Les droits d’un utilisateur sont la combinaison de plusieurs statuts, pas d’un seul rôle.
8. L’administration peut corriger manuellement presque tout état opérationnel important.
9. Toutes les actions critiques doivent laisser une trace exploitable.

## Vocabulaire métier

### Compte

Un compte représente une personne autorisée à se connecter.

### Série

Une série est une règle récurrente hebdomadaire permettant de générer des occurrences futures.

### Occurrence

Une occurrence est une séance concrète datée, visible dans le calendrier et potentiellement réservable.

### Type d’occurrence

Deux types existent:

- `pratique libre`
- `cours`

### Créneau

Un créneau est une sous-partie temporelle d’une occurrence de pratique libre, utilisée pour la couverture référent.

### Réservation

Une réservation représente l’inscription d’un utilisateur à une occurrence.

### Affectation référent

Une affectation référent représente le fait qu’un utilisateur couvre un créneau de pratique libre.

### Audit

L’audit est le journal des actions métier et système.

## Profils et dimensions d’accès

Le site ne repose pas sur un seul rôle. Un utilisateur cumule plusieurs attributs.

### Attributs d’accès

- `role`: `member` ou `admin`
- `is_active`
- `is_responsable_accredited`
- `has_orange_passport`
- rattachements à des cours
- affectation comme prof sur certaines occurrences ou séries

### Profils utiles à raisonner

### 1. Invité

Peut seulement accéder:

- à la page d’accueil, qui redirige vers login
- à la page de connexion

### 2. Membre simple

Conditions:

- `role = member`
- `is_active = true`
- pas forcément passeport orange
- pas forcément référent
- pas forcément inscrit à un cours

Peut:

- se connecter
- voir le calendrier
- voir le détail des occurrences visibles
- voir ses réservations

Ne peut réserver que si ses droits le permettent.

### 3. Membre avec passeport orange

Peut en plus:

- réserver les occurrences de pratique libre

### 4. Référent accrédité

Peut en plus:

- réserver les occurrences de pratique libre
- prendre la responsabilité d’un créneau libre
- relâcher sa propre responsabilité sur un créneau futur

### 5. Membre rattaché à un cours

Peut en plus:

- réserver les occurrences du cours auquel il est rattaché

### 6. Prof

Ce n’est pas un rôle global stocké. C’est un utilisateur affecté comme prof sur une occurrence ou comme prof par défaut sur une série de cours.

Peut en plus:

- modifier uniquement les occurrences de cours qui lui sont attribuées

Ne peut pas:

- modifier toute la série
- modifier un autre cours
- accéder à l’administration globale

### 7. Administrateur

Conditions:

- `role = admin`

Peut:

- accéder à tous les écrans admin
- gérer les comptes
- gérer les droits
- créer et modifier séries, occurrences, créneaux
- affecter ou retirer un référent
- corriger les réservations
- consulter l’audit
- configurer les emails automatiques

L’admin a aussi les droits membres utiles:

- accès à toutes les occurrences
- réservation possible
- couverture de créneaux possible
- accès à tous les cours

## Matrice des droits par type de séance

### Pratique libre

Un utilisateur peut réserver si:

- il est actif
- l’occurrence est ouverte
- l’occurrence n’a pas commencé
- il reste de la place
- il n’a pas déjà une réservation active
- et il est dans un des cas suivants:
  - admin
  - référent accrédité
  - détenteur du passeport orange

Un utilisateur peut couvrir un créneau si:

- il est actif
- il est admin ou référent accrédité
- le créneau est une pratique libre
- le créneau n’est pas annulé
- le créneau n’est pas passé
- aucun autre référent actif n’occupe déjà ce créneau

### Cours

Un utilisateur peut réserver si:

- il est actif
- l’occurrence est ouverte
- l’occurrence n’a pas commencé
- il reste de la place
- il n’a pas déjà une réservation active
- et il est dans un des cas suivants:
  - admin
  - membre rattaché à la série du cours

Il n’existe pas de logique de couverture référent sur un cours.

## Carte des pages à recréer

## 1. `/`

### Rôle

Point d’entrée public.

### Comportement

- si non connecté: redirection vers `/login/`
- si connecté: redirection vers `/sessions/`

## 2. `/login/`

### Rôle

Page de connexion club.

### Public

- accessible sans authentification

### Fonction

Permet de se connecter avec:

- `Prénom`
- `Nom`
- `Code`

### Règles

- la connexion ne se fait pas via email
- le nom est normalisé sans accents ni caractères spéciaux
- un compte inactif est refusé
- si le mot de passe est temporaire ou à réinitialiser, l’utilisateur est redirigé vers la page d’activation

## 3. `/password/`

### Rôle

Page obligatoire d’activation ou de réinitialisation du compte.

### Public

- réservée à un utilisateur connecté avec mot de passe non actif

### Fonction

Permet de:

- renseigner l’email du compte
- remplacer le code temporaire par un code personnel

### Règles

- inaccessible à un utilisateur déjà actif
- tant que cette étape n’est pas terminée, l’utilisateur ne peut pas accéder au reste du site

## 4. `/sessions/`

### Rôle

Page principale du site côté membre.

### Public

- réservée aux utilisateurs connectés

### Fonction

Affiche un calendrier hebdomadaire unique contenant toutes les occurrences visibles.

### Contenu minimal

- navigation semaine précédente / suivante
- semaine courante
- légende
- grille horaire
- occurrences de la semaine
- une occurrence sélectionnée
- détail inline de l’occurrence sélectionnée

### Règles d’affichage

- plage horaire visible: `08:00` à `23:00`
- semaine affichée: lundi -> dimanche
- par défaut, la semaine courante est affichée
- si aucune occurrence n’est sélectionnée, la première occurrence de la semaine est sélectionnée
- plusieurs occurrences simultanées doivent apparaître comme éléments distincts

### Occurrences visibles

Le calendrier membre affiche les occurrences futures dont le statut est:

- `open`
- `closed`
- `cancelled`

Il n’affiche pas:

- `draft`
- `completed`
- les occurrences passées

### Information minimale dans la grille

Pour chaque occurrence:

- horaire court
- libellé court
- distinction visuelle entre `pratique libre` et `cours`
- distinction visuelle des cas `complet` / `annulé`

### Règles de libellé

Si le libellé de l’occurrence est générique, par exemple `Pratique libre`, la grille doit préférer le libellé de la série si celui-ci est plus utile.

## 5. Détail inline dans `/sessions/`

### Rôle

Afficher toutes les informations utiles d’une occurrence et les actions possibles sans quitter le calendrier.

### Contenu minimal

- titre
- date
- horaire
- type de séance
- statut
- places restantes
- notes éventuelles
- prof si c’est un cours
- résumé de couverture référent si c’est une pratique libre
- liste des inscrits
- actions principales

### Actions possibles

Selon le cas:

- `S'inscrire`
- `Se désinscrire`
- `Modifier comme prof`
- prise de responsabilité d’un créneau
- retrait de responsabilité d’un créneau

### Règle de structure

Une seule occurrence détaillée à la fois.

## 6. `/bookings/mine/`

### Rôle

Lister les réservations actives du compte courant.

### Public

- réservé aux utilisateurs connectés

### Fonction

Affiche les occurrences auxquelles l’utilisateur est inscrit.

### Contenu minimal

- date
- horaire
- libellé
- état de confirmation
- lien de retour vers l’occurrence correspondante dans le calendrier

## 7. `/sessions/<occurrence_id>/`

### Rôle

Route legacy de détail.

### Comportement réel attendu

- si l’occurrence est future: redirection vers `/sessions/` avec la semaine et l’occurrence déjà sélectionnées
- cette page ne doit pas être le parcours principal

## 8. `/sessions/teaching/<occurrence_id>/edit/`

### Rôle

Édition prof d’une occurrence de cours.

### Public

- réservé au prof affecté à cette occurrence

### Fonction

Permet de modifier l’occurrence uniquement, pas la série.

### Champs modifiables

- libellé
- date
- heure de début
- heure de fin
- capacité
- statut
- notes

### Champs non modifiables

- type de séance
- série liée
- prof affecté

### Règle d’accès

- 404 si l’utilisateur n’est pas le bon prof
- 404 si l’occurrence n’est pas un cours
- les admins n’utilisent pas ce parcours

## 9. `/admin/sessions/`

### Rôle

Écran principal de pilotage des séances côté admin.

### Contenu minimal

- liste des séries
- liste d’occurrences récentes
- actions de création
- actions d’édition
- actions de statut
- accès aux inscrits
- accès à l’audit

### Finalité

Donner un cockpit opérationnel rapide.

## 10. `/admin/sessions/series/new/`

### Rôle

Créer une série récurrente.

### Champs métier

- libellé
- type de séance
- prof par défaut si cours
- jour de semaine
- heure de début
- heure de fin
- capacité par défaut
- actif

## 11. `/admin/sessions/series/<series_id>/edit/`

### Rôle

Modifier une série récurrente.

### Fonction

Mettre à jour les occurrences liées à la série.

### Cas particulier pratique libre

Doit aussi afficher les occurrences liées avec leurs créneaux, pour correction rapide.

### Actions liées aux créneaux

- corriger heure début / fin
- corriger capacité
- changer le statut du créneau
- affecter un référent
- retirer un référent
- supprimer un créneau

## 12. `/admin/sessions/occurrences/new/`

### Rôle

Créer une occurrence unitaire.

### Champs métier

- série éventuelle
- libellé
- date
- heure début
- heure fin
- capacité
- type
- prof si cours
- statut
- notes

## 13. `/admin/sessions/occurrences/<occurrence_id>/edit/`

### Rôle

Modifier une occurrence unique.

### Fonction

Permet de:

- modifier l’occurrence
- changer rapidement son statut
- supprimer l’occurrence
- voir son contexte métier
- corriger ses créneaux si c’est une pratique libre

### Cas pratique libre

La page doit afficher:

- le résumé de couverture
- la liste des créneaux
- les actions de correction

### Cas cours

La page doit afficher:

- le prof
- l’absence de logique référent

## 14. `/admin/bookings/sessions/<occurrence_id>/`

### Rôle

Correction manuelle des inscriptions d’une occurrence.

### Fonction

Permet de:

- voir les inscrits
- ajouter un inscrit
- retirer un inscrit
- repérer les incohérences de droits

### Incohérences à signaler

- réservation sur pratique libre alors que le droit actuel a été retiré
- réservation sur cours alors que le rattachement au cours n’est plus actif

## 15. `/admin/accounts/`

### Rôle

Gestion des comptes et des droits.

### Fonction

Permet de:

- créer un compte
- importer un lot d’adhérents
- activer / désactiver un compte
- choisir `member` ou `admin`
- donner / retirer l’accréditation référent
- donner / retirer le passeport orange
- rattacher à un ou plusieurs cours
- réinitialiser le code temporaire

## 16. `/admin/accounts/email-automation/`

### Rôle

Configurer les automatismes email.

### Fonction

Permet de régler:

- délai de rappel
- délai d’annulation automatique
- sujet et corps du rappel
- sujet et corps de l’email d’annulation

## 17. `/admin/audit/sessions/<occurrence_id>/`

### Rôle

Afficher la chronologie des événements liés à une occurrence.

### Fonction

Permet d’expliquer une situation et de vérifier les corrections.

### Contenu minimal

- date/heure
- type d’événement
- acteur humain ou système
- créneau si concerné
- données utiles
- motif

## Règles métier des comptes

## Création de compte

Un compte créé manuellement par l’admin contient au minimum:

- nom complet
- rôle
- statut actif/inactif
- options de droits
- éventuellement email

Le compte est créé avec:

- un code temporaire
- un état de mot de passe non actif

## Réinitialisation de compte

La réinitialisation remet:

- un code temporaire
- un état `reset_required`

## Désactivation de compte

Un compte inactif:

- ne peut pas se connecter
- ne peut pas réserver
- ne peut pas couvrir de créneau

## Normalisation d’identité

Le site doit retrouver un utilisateur à partir de `prénom + nom` en ignorant:

- accents
- apostrophes
- espaces en trop
- casse
- caractères spéciaux

## Règles métier des séries et occurrences

## Série

Une série représente un modèle hebdomadaire.

### Règles

- capacité strictement positive
- fin strictement après début
- une série de pratique libre n’a pas de prof
- une série de cours peut avoir un prof par défaut

### Effet de création

Créer une série génère automatiquement des occurrences futures.

### Nombre d’occurrences générées

Comportement actuel:

- `8` semaines futures

## Occurrence

Une occurrence représente une séance datée.

### Champs métier

- série facultative
- libellé
- date
- heure début
- heure fin
- capacité
- type
- prof éventuel
- statut
- notes

### Statuts utiles

- `draft`
- `open`
- `closed`
- `cancelled`
- `completed`

### Règles

- capacité > 0
- fin > début
- si liée à une série, le type doit rester cohérent avec la série
- une pratique libre n’a pas de prof
- plusieurs occurrences peuvent coexister au même moment

## Règles de propagation série -> occurrences

Quand on modifie une série, les occurrences liées sont réalignées sur:

- le libellé
- le jour cible
- les horaires
- la capacité
- le type
- le prof par défaut selon le cas

## Override d’occurrence

Le produit supporte l’idée qu’une occurrence puisse être modifiée individuellement même si elle appartient à une série.

Point à figer dans la réécriture:

- le statut exact d’un override vis-à-vis d’une future modification de série doit être décidé explicitement

## Règles métier des créneaux

## Existence des créneaux

Les créneaux n’existent que pour les occurrences de `pratique libre`.

Les cours n’ont pas de créneaux référent.

## Découpage automatique

Une occurrence de pratique libre longue est découpée automatiquement en créneaux de `90 minutes maximum`.

Exemple:

- `19:00 -> 22:00`
- devient `19:00 -> 20:30` puis `20:30 -> 22:00`

## Créneau sans réservation propre

Le créneau n’est pas une unité de réservation pratiquant.

Conséquences:

- la jauge du créneau n’est pas autonome
- les réservations restent attachées à l’occurrence entière
- les créneaux servent à la couverture référent et aux automatismes

## Règles de correction manuelle

L’admin peut corriger un créneau:

- heure de début
- heure de fin
- capacité
- statut

### Contraintes

- le créneau doit rester inclus dans l’occurrence
- la durée doit rester <= `90 minutes`
- les créneaux d’une même occurrence ne doivent pas se chevaucher

## Suppression de créneau

Le produit autorise de supprimer tous les créneaux d’une occurrence libre et de conserver malgré tout l’occurrence.

Conséquence:

- une pratique libre peut exister sans aucun créneau référent

## Règles métier des réservations

## Objet réservé

Le pratiquant réserve une `occurrence`.

Il ne réserve pas un créneau.

## Conditions nécessaires pour réserver

1. utilisateur connecté et actif
2. occurrence `open`
3. occurrence non commencée
4. capacité restante > 0
5. pas déjà une réservation active sur cette occurrence
6. droit d’accès compatible avec le type

## Cas `pratique libre`

Condition supplémentaire:

- admin, ou référent accrédité, ou passeport orange

## Cas `cours`

Condition supplémentaire:

- admin, ou rattachement actif à la série du cours

## Refus à expliciter dans l’UI

Le site doit afficher clairement les cas suivants:

- séance annulée
- séance terminée
- séance non ouverte
- séance déjà commencée
- séance complète
- droit manquant à la pratique libre
- absence de rattachement au cours
- déjà inscrit

## Désinscription

Une réservation peut être annulée tant que l’occurrence n’a pas commencé.

Point important:

- l’occurrence n’a pas besoin d’être `open` pour permettre l’annulation
- une occurrence future `closed` peut encore être quittée

## Correction manuelle admin

L’admin peut ajouter une réservation manuelle sur une occurrence future même si elle est `closed`.

L’ajout manuel reste interdit si:

- l’occurrence est annulée
- l’occurrence est terminée
- l’occurrence a déjà commencé
- l’occurrence est complète
- l’utilisateur est déjà inscrit

## Règles métier de couverture référent

## Prise de responsabilité

Un utilisateur peut prendre un créneau si:

1. il est admin ou référent accrédité
2. le créneau appartient à une pratique libre
3. le créneau n’est pas annulé
4. le créneau n’est pas terminé
5. le créneau n’a pas commencé
6. aucun référent actif n’est déjà affecté

## Retrait de responsabilité

Un utilisateur peut quitter un créneau si:

- il est lui-même le référent actif
- le créneau n’a pas commencé

## Indépendance vis-à-vis de l’inscription pratiquant

Un même utilisateur peut:

- être inscrit comme pratiquant sur l’occurrence
- et couvrir un créneau

Quitter la responsabilité ne retire pas la réservation pratiquant.

## Réaffectation admin

L’admin peut:

- affecter manuellement un référent à un créneau
- retirer le référent actuel
- réaffecter un créneau déjà couvert

La réaffectation admin révoque l’affectation précédente.

## Retrait d’accréditation référent

Quand l’admin retire l’accréditation référent à un utilisateur:

- les affectations futures actives de cet utilisateur sont automatiquement révoquées

## Règles métier des cours

## Rattachement à un cours

Le rattachement à un cours donne le droit de réserver les occurrences de cette série.

Il ne crée pas d’inscription automatique.

## Édition prof

Le prof peut modifier une occurrence de son propre cours, occurrence par occurrence.

Il ne peut pas:

- modifier les autres cours
- modifier la série complète
- modifier la structure globale des droits

## Règles du calendrier

## Vue unique

Le calendrier doit mélanger sur la même semaine:

- pratiques libres
- cours

## Collision visuelle

Si plusieurs occurrences se chevauchent:

- elles doivent rester distinctes et sélectionnables

## Focus membre

Le calendrier doit rester compréhensible sur smartphone.

La grille ne doit contenir que l’information minimale.

Le détail complet vit dans le panneau inline.

## État vide

Si une semaine ne contient aucune occurrence visible:

- le site affiche un état vide explicite

## Libellés importants à afficher

Le calendrier et le détail doivent rendre visibles:

- le type de séance
- le prof si cours
- le manque de référent si pratique libre
- l’annulation
- la fermeture
- la complétude

## Règles d’import des comptes

## Format

Le produit supporte un import TSV.

Colonnes observées:

- `Prénom`
- `Nom`
- `Créneau`
- `Commentaire`
- `Passeport orange`
- `Référent salle`

## Effets

L’import peut:

- créer un compte
- réactiver un compte membre existant
- donner le passeport orange
- donner l’accréditation référent
- rattacher à un cours

## Limitations actuelles à connaître

- si deux lignes du même import décrivent la même personne, c’est rejeté comme doublon
- un admin existant ne peut pas être modifié par l’import
- le format actuel n’est pas idéal pour exprimer plusieurs cours sur une même personne

## Emails automatiques

## Paramétrage

L’admin choisit:

- combien de jours avant la séance envoyer le rappel
- combien de jours avant la séance annuler automatiquement
- le texte des emails

## Rappel de couverture

Le système envoie un rappel quand:

- un créneau de pratique libre est non couvert
- il reste exactement `reminder_days_before` jours
- aucun rappel n’a déjà été envoyé pour ce créneau

Destinataires:

- tous les référents accrédités actifs
- tous les admins actifs

## Annulation automatique

Le système annule un créneau quand:

- le créneau de pratique libre est non couvert
- il reste `cancellation_days_before` jours ou moins
- le créneau n’est pas déjà annulé

Effets:

- statut du créneau -> `cancelled`
- horodatage d’auto-annulation
- envoi d’un email d’annulation
- création d’événements d’audit

## Destinataires de l’email d’annulation

Les emails d’annulation sont envoyés aux inscrits de l’occurrence.

Cela est cohérent avec la règle fondamentale:

- les inscriptions sont portées par l’occurrence, pas par le créneau

## Audit

## Objet

Le site doit permettre d’expliquer après coup ce qui s’est passé sur une occurrence.

## Ce qui doit être audité

Au minimum:

- création / modification de compte
- reset de code
- attribution / retrait du passeport orange
- attribution / retrait de l’accréditation référent
- attribution / retrait de rattachement à un cours
- création / modification de série
- création / modification / suppression d’occurrence
- changement de statut d’occurrence
- création / modification / suppression de créneau
- changement de statut de créneau
- prise / retrait / révocation de responsabilité référent
- création / annulation de réservation
- ajout / retrait manuel de réservation
- édition d’occurrence par un prof
- rappel automatique
- annulation automatique
- notification automatique

## Structure minimale d’un événement

- acteur
- rôle de l’acteur au moment de l’action
- type d’action
- cible
- occurrence liée si applicable
- créneau lié si applicable
- motif si fourni
- métadonnées utiles
- date/heure

## Règles de suppression

## Suppression d’occurrence

Le produit actuel autorise la suppression d’une occurrence même si elle possède:

- des réservations
- des affectations référent

L’UI doit prévenir clairement, mais le backend supprime effectivement l’ensemble lié.

## Suppression de série

Le produit actuel autorise la suppression d’une série et de toutes ses occurrences, même si elles ont des réservations ou des affectations.

L’UI doit prévenir clairement.

## Éléments non requis

Pour reconstruire le site à l’identique fonctionnel, il ne faut pas introduire par défaut:

- liste d’attente
- promotion automatique depuis liste d’attente
- réservation par créneau
- réservation automatique sur un cours après rattachement
- ouverture automatique d’une pratique libre conditionnée à la couverture référent
- logique native mobile

## Invariants à préserver

1. Connexion par prénom + nom + code.
2. Normalisation des noms sans accents ni caractères spéciaux.
3. Forçage du changement de code si compte non activé.
4. Calendrier hebdomadaire unique comme écran central.
5. Détail inline sur la même page.
6. Distinction forte entre `pratique libre` et `cours`.
7. Réservation portée par l’occurrence.
8. Couverture référent portée par le créneau.
9. Maximum un référent actif par créneau.
10. Créneaux de pratique libre limités à `90 minutes`.
11. Gestion des droits par combinaison de statuts.
12. Corrections manuelles admin.
13. Audit exploitable.
14. Emails automatiques paramétrables.

## Décisions à figer explicitement avant réécriture

Le produit actuel laisse quelques zones grises qu’il faut trancher proprement dans la future version.

### 1. Comportement exact des overrides de série

Le système supporte l’idée qu’une occurrence soit modifiée seule, mais la règle de non-réalignement futur doit être explicitement définie.

### 2. Pouvoir exact de l’admin sur les créneaux

Le backend actuel laisse une grande liberté de correction admin. Il faut décider jusqu’où elle doit aller.

### 3. Statut métier réel de `is_active` sur les séries

Le champ existe, mais son effet fonctionnel est faible. Il faut décider s’il devient un vrai levier ou s’il disparaît.

### 4. Format cible de l’import adhérents

L’import actuel fonctionne, mais il est limité. Il faut décider si on le reproduit tel quel ou si on l’améliore.

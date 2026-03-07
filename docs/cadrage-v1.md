# Cadrage V1 - Inscriptions seances de pratique libre

## 1. Objectif

Construire une V1 simple permettant de gerer les inscriptions aux seances de pratique libre de la section escalade de l'USMV, avec les contraintes suivantes :

- acces reserve aux grimpeurs autorises
- presence d'au moins un coordinateur sur chaque seance
- capacite limitee selon le jour et le contexte
- gestion d'une liste d'attente
- notifications automatiques de base

L'objectif n'est pas de refaire le site d'inscription USMV, mais de couvrir le besoin specifique des seances libres.

## 2. Probleme a resoudre

Aujourd'hui, Benoit veut ouvrir des seances de pratique libre, mais il manque un outil pour :

- publier les dates ouvertes
- identifier les coordinateurs par creneau
- laisser s'inscrire uniquement les grimpeurs eligibles
- limiter les inscriptions selon la capacite reelle
- gerer les desistements sans traitement manuel

Le besoin central est donc une reservation controlee, pas une application communautaire generaliste.

## 3. Utilisateurs V1

### Administrateur

Personne qui configure les creneaux, valide les utilisateurs, gere les coordinateurs, ouvre ou ferme des seances, et traite les exceptions.

### Coordinateur

Adherent autorise a coordonner une seance libre. Il ne supervise pas techniquement la pratique, mais il :

- s'engage a etre present
- verifie la presence et l'eligibilite des inscrits
- peut signaler un remplacement ou une indisponibilite

### Grimpeur autonome

Adherent autorise a s'inscrire aux seances libres, en pratique titulaire du passeport orange.

## 4. Regles metier deduites des mails

### Eligibilite

- Seuls les grimpeurs autorises peuvent s'inscrire aux seances libres.
- En l'etat des mails, cela signifie au minimum : titulaire du passeport orange.
- Les coordinateurs doivent eux aussi avoir au moins le passeport orange.
- L'acces a l'app doit etre filtre pour eviter les inscriptions de personnes non eligibles.

### Coordination

- Chaque creneau recurrent doit avoir idealement 2 a 3 coordinateurs identifies.
- Ces coordinateurs s'inscrivent a l'avance sur chaque date future.
- Une seance ne devrait probablement etre ouverte aux grimpeurs que si au moins un coordinateur est confirme.
- Si aucun coordinateur ne peut venir, un remplacement doit etre trouve dans un pool de coordinateurs.

### Capacite

- Objectif metier : ne pas depasser 15 cordees dans la salle.
- Les mails utilisent ensuite une logique de "places" avec :
  - 16 places la plupart des soirs en parallele d'un cours adulte
  - 30 places le lundi soir, sans cours adulte
- Ce point doit etre clarifie car "15 cordees" et "16 places" ne designent pas la meme unite.

### Liste d'attente

- Si une seance est complete, les inscrits suivants vont en liste d'attente.
- En cas de desistement, la premiere personne en attente doit etre notifiee.
- Sans reponse ou en cas de refus, la proposition passe a la suivante.

### Week-end

- Le meme principe doit pouvoir s'appliquer a des seances du week-end.

## 5. Incoherences ou ambiguities a lever

### Unite de capacite

Le plus gros point flou est l'unite de reservation :

- soit on reserve des personnes
- soit on reserve des binomes / cordees

Les mails parlent de :

- limite de 15 cordees dans la salle
- diminution de 7 cordees si un cours adulte a lieu en parallele
- mais aussi de 16 places et 30 places

Ces chiffres ne sont coherents que si "places" veut dire "grimpeurs" et non "cordees". Dans ce cas :

- capacite standard sans cours : 30 grimpeurs = 15 cordees
- capacite avec cours adulte de 7 cordees : il resterait 16 grimpeurs, donc 8 cordees

Il faut donc choisir explicitement le modele V1 :

1. V1 reserve des personnes
2. V1 reserve des binomes constitues

Recommendation V1 : reserver des personnes, pas des binomes. C'est beaucoup plus simple a exploiter, a comprendre et a administrer.

## 6. Proposition de perimetre V1

### Inclus dans la V1

- connexion utilisateur
- gestion des roles : admin, coordinateur, grimpeur
- gestion de l'eligibilite "passeport orange"
- gestion de creneaux recurrents
- generation des dates de seance a venir
- affectation des coordinateurs a chaque date
- ouverture ou fermeture d'une seance
- inscription et desinscription a une seance
- capacite maximale par seance
- liste d'attente ordonnee
- promotion automatique depuis la liste d'attente
- notifications email
- feuille de presence simple pour le coordinateur
- back-office admin pour corrections manuelles

### Exclu de la V1

- application mobile native iOS / Android
- paiement en ligne
- integration forte avec le site USMV
- synchronisation automatique des licences / passeports
- WhatsApp, SMS ou push mobile
- gestion complexe des binomes ou partenaires
- signature de decharge
- statistiques avancees

## 7. Approche technique recommandee

### Produit

Faire une application web responsive, utilisable sur mobile, plutot qu'une application native.

Pourquoi :

- zero cout de publication sur stores
- zero friction d'installation
- un seul codebase
- suffisant pour un usage "ouvrir un creneau, s'inscrire, recevoir un email"
- compatible avec la demande "sur tel mobile" sans surinvestir

Option utile mais secondaire : rendre l'application installable en pseudo-app via PWA plus tard.

### Architecture

Recommendation pragmatique pour un projet benevole :

- frontend + backend web unifies
- interface admin integree
- base relationnelle simple
- envoi d'emails via SMTP
- taches planifiees pour la liste d'attente

### Stack suggeree

Django est un bon candidat pour cette V1 :

- authentification et gestion utilisateurs prêtes vite
- interface d'administration native tres utile pour un projet benevole
- modelisation metier simple et robuste
- rendu HTML server-side suffisant pour une UX mobile correcte
- peu de JavaScript necessaire

Stack concrete possible :

- Django
- PostgreSQL en production, SQLite possible au debut
- templates serveur + CSS simple
- SMTP pour emails
- cron ou job planifie pour expiration des offres de liste d'attente

Si l'equipe prefere JavaScript, une stack type Next.js + Postgres est faisable, mais elle apportera plus de complexite pour moins de valeur immediate.

## 8. Modele de donnees V1

### User

- nom
- prenom
- email
- telephone optionnel
- actif / inactif

### UserRole

- user
- role : admin / coordinateur / grimpeur

### Eligibility

- user
- passeport_orange : oui / non
- date_validation
- valide_par

### SlotTemplate

Creneau recurrent, par exemple "mercredi 20h-22h".

- jour_semaine
- heure_debut
- heure_fin
- type_seance
- capacite_par_defaut
- actif

### SessionOccurrence

Date concrete d'un creneau.

- slot_template
- date
- statut : brouillon / ouverte / complete / fermee / annulee
- capacite
- nb_coordinateurs_min
- commentaire

### SessionCoordinator

- session_occurrence
- user
- statut : propose / confirme / remplace / absent

### Booking

- session_occurrence
- user
- statut : confirme / attente / annule / refuse
- position_attente
- date_inscription
- date_reponse_limite si proposition depuis attente

### AuditEvent

- type_evenement
- user_concerne
- session_concernee
- metadata minimale
- created_at

## 9. Regles fonctionnelles recommandees pour la V1

### Ouverture d'une seance

- Une seance peut etre generee automatiquement depuis un creneau recurrent.
- Elle n'est ouvrable aux grimpeurs que si au moins un coordinateur est confirme.

### Inscription

- Un utilisateur ne peut avoir qu'une seule inscription par seance.
- Si la capacite est atteinte, il passe en liste d'attente.
- Un utilisateur non eligible ne peut pas s'inscrire.

### Desistement

- Si un inscrit confirme annule, la premiere personne en attente recoit une proposition.
- La proposition expire au bout d'un delai configurable.
- Sans reponse, la place est proposee au suivant.

### Presence

- Le coordinateur consulte la liste des inscrits.
- Il peut marquer "present" ou "absent" dans une vue simple.

## 10. Notifications V1

Canaux recommandes :

- email uniquement en V1

Evenements notifies :

- confirmation d'inscription
- passage en liste d'attente
- proposition de place depuis la liste d'attente
- rappel avant la seance
- annulation de seance
- alerte aux coordinateurs en cas d'absence de coordinateur confirme

Ne pas partir sur WhatsApp en V1 :

- cout et complexite plus eleves
- contraintes API
- maintenance inutile pour une premiere version

## 11. Ecrans V1

### Cote grimpeur

- connexion
- liste des seances ouvertes
- detail d'une seance
- s'inscrire / se desinscrire
- voir son statut : confirme ou attente

### Cote coordinateur

- mes seances a venir
- confirmer ma presence
- voir la liste des inscrits
- signaler un besoin de remplacement

### Cote admin

- tableau des creneaux recurrents
- calendrier des seances
- gestion des utilisateurs et eligibilites
- gestion des coordinateurs
- ajustement manuel des inscriptions

## 12. Questions a trancher avant la premiere spec detaillee

### Gouvernance et usage

- Qui administre l'outil au quotidien ?
- Qui peut valider qu'un adherent a bien le passeport orange ?
- Qui peut nommer ou retirer un coordinateur ?

### Authentification

- Les utilisateurs creent-ils eux-memes leur compte ?
- Ou bien l'admin importe-t-il une liste initiale d'adherents ?
- L'email est-il obligatoire et fiable pour tous ?

### Eligibilite

- L'outil gere-t-il seulement "passeport orange oui/non" ?
- Faut-il distinguer plusieurs niveaux plus tard ?
- Un adherent sans passeport orange peut-il au moins voir les seances sans s'inscrire ?

### Capacite

- La reservation se fait-elle par personne ou par cordee ?
- Le chiffre de reference est-il 30 personnes / 15 cordees ?
- Le "16" correspond-il bien a 16 personnes les soirs avec cours adulte ?

### Coordinateurs

- Faut-il au moins 1 coordinateur confirme, ou 2, pour ouvrir une seance ?
- Les coordinateurs sont-ils rattaches a un jour fixe ou choisis librement date par date ?
- Le remplacement passe-t-il par l'outil ou seulement par organisation humaine puis mise a jour manuelle ?

### Liste d'attente

- Quel delai laisser pour accepter une place liberee ? 2h, 6h, 24h ?
- Faut-il accepter automatiquement la personne suivante si la precedente ne repond pas ?
- Une proposition doit-elle etre faite a une seule personne a la fois, ou a plusieurs en parallele ?

### Calendrier

- Combien de semaines a l'avance ouvre-t-on les inscriptions ?
- Peut-on s'inscrire jusqu'a quelle heure avant le debut de la seance ?
- Peut-on annuler jusqu'a quelle heure sans intervention admin ?

### Mobile

- Le besoin reel est-il "application mobile" ou simplement "outil pratique sur telephone" ?

## 13. Recommendation de demarrage

Pour lancer le projet proprement, je recommande de figer d'abord les choix suivants :

1. Web responsive, pas d'app native en V1
2. Reservation par personne, pas par cordee
3. Email comme seul canal de notification en V1
4. Ouverture d'une seance uniquement si au moins un coordinateur est confirme
5. Admin manuel de l'eligibilite et des coordinateurs
6. Liste d'attente sequentielle, une proposition a la fois avec expiration

## 14. Proposition de premiere spec fonctionnelle

La premiere spec detaillee peut ensuite porter sur ce lot unique :

- gestion des utilisateurs eligibles
- creation des creneaux recurrents
- generation des seances
- affectation des coordinateurs
- inscription / desinscription
- liste d'attente
- notifications email
- back-office admin

Ce lot est suffisamment petit pour produire une vraie V1, et suffisamment complet pour etre utilise en conditions reelles.

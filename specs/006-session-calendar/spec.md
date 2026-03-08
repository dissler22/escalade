# Feature Specification: Vue calendaire hebdomadaire des seances

**Feature Branch**: `006-session-calendar`  
**Created**: 2026-03-08  
**Status**: Draft  
**Input**: User description: "Le but et de faire la spec 5 : rendre la vu dans séance calendaire. je veux donc une vue calendaire de 8h à 23h par semaine. Ensuite on minimise le texte (exemple non obligatoire : pratique libre), on place ce qui était dans voir la séance en dessous au lieu de dans un autre onglet pour limiter les changement de page. On oublie pas de privilegier la simplicité et lisibilité, les details seront donc en dessous pas séance."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consulter la semaine en un coup d oeil sur smartphone (Priority: P1)

Un adherent ouvre la web app sur son telephone et arrive sur une vue calendaire hebdomadaire qui affiche les seances entre 8h et 23h. Il comprend rapidement quel jour et a quelle heure se trouvent les seances a venir, sans devoir ouvrir une fiche separee pour reperer l information essentielle.

**Why this priority**: La valeur principale de la demande est d accelerer la lecture du planning hebdomadaire et de reduire les changements de page sur le parcours adherent principal.

**Independent Test**: Sur smartphone, un adherent connecte ouvre l ecran des seances, identifie une seance de la semaine voulue dans la grille, comprend son statut essentiel et sait laquelle selectionner sans quitter la vue calendaire. Ce flux livre deja de la valeur meme avant d affiner les details inline.

**Acceptance Scenarios**:

1. **Given** un adherent connecte consulte les seances de la semaine courante, **When** la vue calendaire s affiche, **Then** il voit une grille hebdomadaire couvrant chaque jour de la semaine et une plage horaire de 8h a 23h.
2. **Given** plusieurs seances sont ouvertes dans la semaine, **When** l adherent parcourt la grille, **Then** chaque seance apparait au bon jour et sur le bon intervalle horaire avec un libelle volontairement court et lisible.
3. **Given** une seance est complete, annulee ou sans responsable sur un creneau, **When** elle apparait dans le calendrier, **Then** son etat essentiel reste identifiable sans avoir a ouvrir une autre page.

---

### User Story 2 - Voir et utiliser les details sans changer de page (Priority: P2)

Un adherent touche une seance dans la grille hebdomadaire et voit immediatement les informations detaillees s afficher plus bas sur le meme ecran. Il peut ensuite reserver, annuler sa reservation ou gerer son role de responsable depuis cette zone detaillee sans naviguer vers une fiche de seance separee.

**Why this priority**: Une fois la lecture de la semaine simplifiee, la seconde valeur est de concentrer la consultation et l action sur un ecran unique, ce qui reduit la friction du parcours mobile.

**Independent Test**: Depuis la vue hebdomadaire, un adherent selectionne une seance, lit ses informations detaillees dans la zone inferieure, puis effectue une action deja autorisee. Il obtient le resultat attendu sans ouvrir une page de detail distincte.

**Acceptance Scenarios**:

1. **Given** un adherent consulte la vue hebdomadaire, **When** il selectionne une seance dans la grille, **Then** les details de cette seance s affichent sous le calendrier sur la meme page.
2. **Given** l adherent a deja une reservation sur la seance selectionnee, **When** il consulte la zone detaillee, **Then** il y retrouve l action de desinscription et les informations utiles a sa decision.
3. **Given** l adherent est accredite pour couvrir des creneaux responsables, **When** il consulte la zone detaillee d une seance selectionnee, **Then** il peut y voir et utiliser les actions de prise ou d abandon de responsabilite deja autorisees.

---

### User Story 3 - Garder une interface sobre et lisible meme quand la semaine est chargee (Priority: P3)

Un adherent ou un administrateur veut une interface qui reste simple a lire meme lorsqu il y a plusieurs seances, plusieurs statuts et des textes metier deja existants. La grille garde donc uniquement l information essentielle, tandis que les details complets restent regroupes dans la partie inferieure.

**Why this priority**: La demande insiste sur la simplicite et la lisibilite. Ce travail vient apres le flux principal, car il consolide l ergonomie lorsque le planning devient plus dense.

**Independent Test**: Avec une semaine contenant plusieurs seances et etats differents, un testeur verifie que la grille reste compacte, que les libelles redondants ne saturent pas l affichage et qu une seule zone detaillee concentre les informations longues sans confusion.

**Acceptance Scenarios**:

1. **Given** une semaine contient plusieurs seances avec des informations longues, **When** elles s affichent dans le calendrier, **Then** la grille ne conserve que les libelles essentiels et renvoie le detail complet dans la zone inferieure.
2. **Given** l utilisateur change de semaine ou selectionne une autre seance, **When** la nouvelle seance est choisie, **Then** la zone detaillee se met a jour clairement sans multiplier les panneaux ouverts simultanement.

### Edge Cases

- Deux seances se chevauchent partiellement le meme jour: la vue doit permettre de distinguer clairement les deux seances sans masquer l une d elles.
- Une seance commence avant 8h ou finit apres 23h: seule la partie comprise dans la plage visible est montree clairement, sans faire disparaitre le fait qu elle sort du cadre horaire.
- Une semaine ne contient aucune seance ouverte: l utilisateur doit comprendre immediatement qu il n y a rien a reserver pour cette semaine.
- Une seance a un titre ou des statuts trop longs pour tenir proprement dans la grille: le calendrier doit rester lisible sans tronquer l information critique de maniere trompeuse.
- L utilisateur touche plusieurs seances successivement sur smartphone: l ecran doit conserver un seul detail principal visible a la fois pour eviter la confusion.
- La connexion mobile est faible au moment de la selection d une seance: l utilisateur doit conserver le contexte de la semaine et comprendre si les details n ont pas encore ete rafraichis.

## Requirements *(mandatory)*

### Roles & Rules

- **Actor Roles**:
  - `Adherent`: consulte la vue hebdomadaire, selectionne une seance, reserve, annule et consulte les informations utiles sans changer de page.
  - `Responsable accredite`: fait les memes actions qu un adherent et peut en plus prendre ou abandonner un creneau responsable depuis le detail inline de la seance.
  - `Administrateur`: continue de creer, modifier, ouvrir, fermer et corriger les seances depuis les parcours d administration existants; il verifie aussi que l affichage adherent reste lisible.
- **Explicit Permissions**:
  - Un adherent ou responsable accredite peut voir uniquement les seances et actions deja autorisees par les specs precedentes.
  - Un responsable accredite n obtient aucun droit d administration supplementaire dans cette spec.
  - Un administrateur conserve les droits d administration existants; cette spec ne lui donne pas de nouveaux pouvoirs metier, seulement une presentation adherent differente.
  - Toute action non explicitement autorisee par les specs 001 et 004 reste interdite.
- **Resolved Business Rules**:
  - Le parcours adherent principal des seances devient une vue calendaire hebdomadaire.
  - La grille affiche une plage horaire fixe de 8h a 23h pour chaque semaine consultee.
  - La grille privilegie les informations courtes et immediatement utiles; les libelles redondants ou peu decisifs dans la grille peuvent etre reduits ou omis.
  - Les informations detaillees et les actions de la seance selectionnee sont affichees sous la grille, sur la meme page.
  - Le parcours principal ne doit plus imposer l ouverture d une fiche de seance separee pour consulter le detail ou agir sur la seance selectionnee.
  - Les regles existantes de reservation, d annulation, de couverture responsable, de permissions et de trace d audit restent inchangees.
- **Open Business Rules**:
  - Aucun point critique ouvert pour cette iteration.

### Functional Requirements

- **FR-001**: Le systeme MUST presenter aux adherents connectes les seances ouvertes dans une vue calendaire affichee semaine par semaine.
- **FR-002**: Le systeme MUST afficher dans cette vue une echelle horaire visible de 8h a 23h pour chaque jour de la semaine.
- **FR-003**: Le systeme MUST positionner chaque seance sur le bon jour et le bon intervalle horaire de la grille hebdomadaire.
- **FR-004**: Le systeme MUST limiter dans la grille le texte a l information essentielle permettant d identifier rapidement une seance et son etat utile.
- **FR-005**: Le systeme MUST distinguer clairement dans la grille au moins les etats qui changent la decision utilisateur, notamment reservable, complet, annule ou creneau responsable non couvert.
- **FR-006**: Le systeme MUST permettre a l utilisateur de passer a la semaine precedente ou suivante sans quitter l ecran de consultation des seances.
- **FR-007**: Le systeme MUST afficher sous le calendrier une zone detaillee pour la seance selectionnee, sur le meme ecran que la grille hebdomadaire.
- **FR-008**: Le systeme MUST faire apparaitre dans cette zone detaillee les informations auparavant necessaires a la consultation de la fiche de seance, y compris les horaires, le statut, la disponibilite, les creneaux responsables et les actions deja autorisees.
- **FR-009**: Le systeme MUST permettre a l adherent d effectuer depuis la zone detaillee les actions deja permises, notamment reserver, annuler sa reservation, prendre un creneau responsable ou l abandonner selon son role.
- **FR-010**: Le systeme MUST conserver une seule seance principale detaillee a la fois afin de privilegier la lisibilite et d eviter l empilement de contenus longs.
- **FR-011**: Le systeme MUST conserver les memes regles metier, permissions et traces d audit que les specs precedentes pour toutes les actions realisees depuis cette nouvelle presentation.
- **FR-012**: Le systeme MUST garder un etat vide explicite quand aucune seance n est disponible sur la semaine affichee.
- **FR-013**: Le systeme MUST rester comprehensible sur smartphone sans imposer de navigation vers une page de detail distincte pour le parcours adherent principal.

### Audit & Operations

- **Audit Events**:
  - Aucun nouvel evenement d audit n est exige par cette spec.
  - Toutes les traces deja requises pour creation, modification, reservation, annulation et responsabilite restent obligatoires lorsque ces actions sont declenchees depuis la vue calendaire.
- **Operational Procedure**:
  - L administrateur continue de preparer les seances et leurs creneaux via les parcours d administration existants.
  - Les adherents consultent ensuite la semaine concernee dans la vue calendaire et choisissent une seance depuis la grille.
  - Les actions courantes se font depuis le detail affiche sous le calendrier, sans multiplier les changements de page.
- **Manual Recovery**:
  - Si une semaine devient exceptionnellement trop dense ou ambigue a lire, l administrateur doit pouvoir verifier les horaires et statuts depuis les ecrans d administration existants pour confirmer l information a communiquer.
  - Si un utilisateur signale un doute apres une action realisee dans le detail inline, l administrateur verifie la reservation, la responsabilite et l historique depuis les vues d administration deja en place puis corrige manuellement si besoin selon les specs precedentes.
  - La fonctionnalite ne doit introduire aucune tache recurrente supplementaire pour l equipe benevole.
- **Cost Impact**:
  - La fonctionnalite ne doit introduire aucun cout recurrent obligatoire supplementaire au dela de l hebergement et des actifs existants deja compatibles avec un budget associatif quasi nul.

### Data & Privacy

- **Collected Data**:
  - aucune nouvelle donnee personnelle obligatoire
  - semaine affichee et seance selectionnee dans le parcours de consultation
  - informations de seance deja existantes: date, horaires, disponibilite, statut, reservations et couverture responsable
- **Purpose of Each Data Item**:
  - la semaine affichee sert a naviguer dans le planning hebdomadaire
  - la seance selectionnee sert a montrer un detail complet sans changer de page
  - les informations de seance existantes servent a permettre la consultation, la reservation et la prise de responsabilite
- **Access Scope**:
  - un adherent ou responsable accredite voit les memes donnees de seance qu aujourd hui selon son role
  - un administrateur conserve l acces complet deja existant dans l administration
- **Retention / Deletion Approach**:
  - Cette spec n ajoute aucune nouvelle retention de donnees personnelles.
  - Les informations deja conservees sur les seances, reservations, responsabilites et traces suivent les regles de retention definies par les specs existantes.

### Key Entities *(include if feature involves data)*

- **Semaine calendaire**: ensemble des jours et horaires visibles par l utilisateur pour consulter les seances entre 8h et 23h.
- **Bloc de seance dans la grille**: representation condensee d une seance dans le calendrier, avec un texte court et un etat essentiel.
- **Detail inline de seance**: zone sous le calendrier qui regroupe les informations completes et les actions de la seance actuellement selectionnee.

### Assumptions

- La vue calendaire hebdomadaire concerne d abord le parcours adherent de consultation des seances ouvertes.
- Les regles metier de reservation et de responsabilite definies par les specs 001 et 004 ne changent pas; seule leur presentation evolue.
- Les sessions de pratique libre continuent d etre consultables semaine par semaine, y compris lorsqu elles sont decoupees en plusieurs creneaux responsables.
- Les informations longues qui ne tiennent pas clairement dans la grille restent accessibles dans le detail inline sans exiger une nouvelle page.
- Le produit peut conserver des parcours d administration distincts si cela n ajoute pas de friction au parcours adherent principal.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur smartphone, au moins 90 % des adherents guides peuvent reperer une seance voulue dans la bonne semaine en moins de 30 secondes.
- **SC-002**: Sur smartphone, au moins 90 % des adherents guides peuvent consulter le detail d une seance puis lancer l action principale attendue en moins de 90 secondes sans ouvrir de page de detail separee.
- **SC-003**: 100 % des seances affichees dans la plage 8h a 23h apparaissent au bon jour et dans le bon ordre horaire de la semaine consultee.
- **SC-004**: 100 % des actions de reservation, d annulation et de responsabilite lancees depuis la vue calendaire continuent de produire les traces d audit deja exigees par les specs precedentes.
- **SC-005**: Le fonctionnement nominal de cette vue hebdomadaire ne requiert aucun service payant supplementaire incompatible avec un budget associatif quasi nul.

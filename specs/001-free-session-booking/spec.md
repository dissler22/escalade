# Feature Specification: Reservations de seances libres

**Feature Branch**: `001-free-session-booking`  
**Created**: 2026-03-07  
**Status**: Draft  
**Input**: User description: "Bien alors pour clarifier : il y a 15 cordees donc 15*2 = 30 place par seance. SI il y a deja 7 cordees prises par le cours adulte il reste plus que 30 - 7*2 = 16 place pour la pratique libre. Donc pour les decision : web mobile, au plus simple reservation par personne, nombre de place definie par ladmin/la personne creant la seance avec la possibilite de creer/modifier une seance reguliere aka toute les semaine et creer/modifier une seance sur une seule semaine. Louverture est faite par les admin, aucune regle venant de lappli, pas de liste dattente, si cest plein on ne peut pas sinscrire. Authentification par compte, on a les adresses mail et les codes temporaires de tout ceux qui peuvent. Pas besoin de prendre en compte les passeport et tout, la verification est deja faite quand on a le compte avec mail et mot de passe."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reserver une place depuis son telephone (Priority: P1)

Un adherent autorise ouvre la web app sur son telephone, se connecte avec son compte, consulte les seances ouvertes a venir, voit le nombre de places restantes et reserve une place sur une seance non complete. Si la seance est deja complete ou fermee, il voit clairement qu'il ne peut pas s'inscrire.

**Why this priority**: C'est le parcours coeur de la V1. Sans ce flux, le produit ne remplit pas son objectif principal.

**Independent Test**: Avec seulement ce parcours, un adherent autorise peut se connecter, voir les seances disponibles, reserver sa place, verifier sa reservation, puis annuler sa reservation sur une future seance. Cela livre deja une valeur exploitable pour le club.

**Acceptance Scenarios**:

1. **Given** un adherent autorise est connecte sur smartphone et une seance est ouverte avec au moins une place restante, **When** il reserve une place, **Then** sa reservation est enregistree et le nombre de places restantes diminue de un.
2. **Given** un adherent autorise est connecte et une seance est complete, **When** il ouvre la fiche de la seance, **Then** il voit que la seance est complete et aucune inscription supplementaire n'est possible.
3. **Given** un adherent autorise a deja une reservation sur une future seance, **When** il annule sa reservation, **Then** la reservation disparait de sa liste personnelle et une place redevient disponible.

---

### User Story 2 - Ouvrir et parametrer les seances (Priority: P2)

Un administrateur cree des seances de pratique libre, soit comme creneau regulier hebdomadaire, soit comme seance ponctuelle, definit le nombre de places disponibles, puis ouvre ou ferme les inscriptions quand il le souhaite.

**Why this priority**: Les adherents ne peuvent pas reserver si les seances ne sont pas creees et publiees. Ce flux doit rester simple et entierement sous controle humain.

**Independent Test**: Avec seulement ce parcours, un administrateur peut creer une seance ponctuelle, creer une serie hebdomadaire, ajuster la capacite a 30 ou 16 places selon le contexte, puis ouvrir ou fermer les inscriptions. Cela permet deja un fonctionnement manuel minimal.

**Acceptance Scenarios**:

1. **Given** un administrateur veut ouvrir un nouveau creneau hebdomadaire, **When** il cree une seance reguliere avec une capacite definie, **Then** les futures occurrences sont preparees avec cette capacite par defaut.
2. **Given** un administrateur gere une semaine particuliere, **When** il cree ou modifie une seule seance de cette semaine, **Then** le changement s'applique uniquement a cette date et n'affecte pas les autres semaines.
3. **Given** une seance existe deja, **When** un administrateur la ferme manuellement, **Then** aucune nouvelle reservation n'est acceptee meme s'il reste des places.

---

### User Story 3 - Corriger manuellement un cas operationnel (Priority: P3)

Un administrateur consulte les reservations d'une seance, corrige une situation manuellement si necessaire et retrouve l'historique des actions importantes pour comprendre ce qui s'est passe.

**Why this priority**: Le club doit pouvoir reprendre la main sans dependre d'une automatisation avancee. C'est essentiel pour un usage benevole fiable.

**Independent Test**: Avec ce seul parcours, un administrateur peut verifier la liste des inscrits, ajouter ou retirer une reservation autorisee en correction manuelle et retrouver les traces des actions liees a la seance.

**Acceptance Scenarios**:

1. **Given** une reservation doit etre corrigee apres une erreur utilisateur, **When** un administrateur ajoute ou retire manuellement une reservation sur une future seance, **Then** l'etat de la seance est corrige et l'action est tracee.
2. **Given** une seance a connu plusieurs creations, reservations et annulations, **When** un administrateur consulte son historique, **Then** il peut voir qui a fait quoi et a quel moment.

### Edge Cases

- Deux adherents tentent de prendre la derniere place presque en meme temps.
- Un adherent tente de reserver deux fois la meme seance.
- Un adherent tente de reserver une seance fermee, annulee ou deja commencee.
- Un administrateur baisse la capacite d'une seance en dessous du nombre deja reserve.
- Une seance reguliere est modifiee apres la creation d'occurrences deja reservees.
- Un administrateur doit corriger une reservation pendant qu'un adherent consulte la meme seance sur smartphone.
- La connexion mobile est faible et l'utilisateur recharge la page apres avoir soumis une reservation.

## Requirements *(mandatory)*

### Roles & Rules

- **Actor Roles**:
  - `Adherent autorise`: se connecte, consulte les seances ouvertes, reserve une place, annule sa propre reservation sur une future seance et consulte ses reservations.
  - `Administrateur`: gere les comptes autorises, cree les seances ponctuelles et regulieres, modifie les capacites, ouvre ou ferme les inscriptions, consulte les reservations, effectue des corrections manuelles et consulte l'historique.
- **Explicit Permissions**:
  - Un adherent autorise peut voir uniquement les seances ouvertes a la reservation et ses propres reservations.
  - Un adherent autorise ne peut pas creer, modifier, ouvrir, fermer ou supprimer une seance.
  - Un administrateur peut creer, modifier, ouvrir, fermer et annuler une seance, ainsi que corriger manuellement les reservations.
  - Toute action non explicitement autorisee par ce document est interdite.
- **Resolved Business Rules**:
  - La reservation se fait par personne, jamais par cordee.
  - La capacite est definie manuellement par un administrateur lors de la creation ou de la modification de la seance.
  - Les valeurs usuelles sont 30 places quand toute la salle est disponible et 16 places quand 7 cordees du cours adulte occupent deja la salle.
  - L'application ne calcule pas automatiquement la capacite a partir des cours adultes; elle applique uniquement la valeur saisie par l'administrateur.
  - L'ouverture et la fermeture des inscriptions sont des decisions manuelles de l'administration.
  - Il n'y a pas de liste d'attente en V1.
  - Si une seance est pleine, aucune inscription supplementaire n'est acceptee.
  - L'eligibilite est geree en amont par l'existence d'un compte autorise; l'application ne gere pas de verification de passeport.
- **Open Business Rules**:
  - Aucun point critique ouvert pour cette V1.

### Functional Requirements

- **FR-001**: Le systeme MUST permettre a chaque utilisateur autorise de se connecter avec un compte nominatif.
- **FR-002**: Le systeme MUST permettre a un administrateur de creer une seance ponctuelle avec au minimum une date, une heure de debut, une heure de fin, un nombre de places et un statut d'ouverture.
- **FR-003**: Le systeme MUST permettre a un administrateur de creer une seance reguliere hebdomadaire avec un jour, un horaire et une capacite par defaut pour les semaines futures.
- **FR-004**: Le systeme MUST permettre a un administrateur de modifier une seance reguliere sans imposer la meme modification a toutes les seances deja creees.
- **FR-005**: Le systeme MUST permettre a un administrateur de creer ou modifier une seule occurrence d'une semaine donnee sans changer les autres semaines.
- **FR-006**: Le systeme MUST permettre a un administrateur d'ouvrir, de fermer ou d'annuler manuellement une seance, sans regle automatique supplementaire.
- **FR-007**: Le systeme MUST afficher aux adherents connectes la liste des futures seances ouvertes, avec au minimum la date, l'horaire, le nombre total de places et le nombre de places restantes.
- **FR-008**: Le systeme MUST permettre a un adherent autorise de reserver une seule place sur une future seance ouverte tant qu'il reste au moins une place disponible.
- **FR-009**: Le systeme MUST empecher une reservation si la seance est complete, fermee, annulee, deja commencee ou si l'utilisateur est deja inscrit.
- **FR-010**: Le systeme MUST permettre a un adherent autorise d'annuler sa propre reservation sur une future seance.
- **FR-011**: Le systeme MUST mettre a jour sans ambiguite le nombre de places restantes apres chaque reservation, annulation ou correction admin.
- **FR-012**: Le systeme MUST permettre a un administrateur de consulter la liste des inscrits d'une seance et le nombre de places encore disponibles.
- **FR-013**: Le systeme MUST permettre a un administrateur d'ajouter ou retirer manuellement une reservation sur une future seance pour corriger un cas operationnel.
- **FR-014**: Le systeme MUST enregistrer une trace horodatee pour chaque creation, modification, ouverture, fermeture ou annulation de seance.
- **FR-015**: Le systeme MUST enregistrer une trace horodatee pour chaque reservation, annulation par l'adherent et correction manuelle par un administrateur.
- **FR-016**: Le systeme MUST rendre l'historique des actions consultable par les administrateurs pour chaque seance.
- **FR-017**: Le systeme MUST signaler clairement a l'utilisateur le resultat de son action sur smartphone, y compris en cas d'echec parce que la seance n'est plus reservable.
- **FR-018**: Le systeme MUST fournir un moyen pour un administrateur de desactiver l'acces d'un compte qui ne doit plus pouvoir reserver.

### Audit & Operations

- **Audit Events**:
  - creation d'une seance ponctuelle
  - creation ou mise a jour d'une seance reguliere
  - creation, modification, ouverture, fermeture, annulation d'une occurrence
  - reservation d'une place
  - annulation d'une reservation par l'adherent
  - ajout manuel d'une reservation par un administrateur
  - retrait manuel d'une reservation par un administrateur
  - desactivation d'un compte
- **Operational Procedure**:
  - L'administrateur cree d'abord les seances regulieres et ponctuelles avec leur capacite.
  - L'administrateur ouvre manuellement les seances qui doivent etre reservables.
  - Les adherents autorises se connectent et reservent eux-memes tant que des places restent disponibles.
  - Si une correction est necessaire, l'administrateur ajuste manuellement la reservation et verifie l'historique.
- **Manual Recovery**:
  - Si une reservation n'a pas abouti clairement, l'administrateur verifie la liste des inscrits et l'historique de la seance.
  - Si l'etat est incorrect, l'administrateur ajoute ou retire la reservation manuellement puis controle le nombre de places restantes.
  - Si une seance a ete ouverte, fermee ou capacitee par erreur, l'administrateur corrige l'etat depuis l'ecran de gestion sans attendre un traitement automatique.
- **Cost Impact**:
  - La fonctionnalite ne doit introduire aucun cout recurrent obligatoire au-dela d'un hebergement web et d'une messagerie deja acceptables pour une association a budget contraint.

### Data & Privacy

- **Collected Data**:
  - identite de compte minimale pour l'acces nominatif
  - email de connexion
  - statut d'activation du compte
  - seances ponctuelles et regulieres
  - capacite de chaque seance
  - reservations par seance
  - historique des actions admin et adherents sur les seances
- **Purpose of Each Data Item**:
  - l'identite et l'email servent a authentifier l'utilisateur et a l'identifier dans les reservations
  - le statut d'activation sert a limiter l'acces aux seules personnes autorisees
  - les donnees de seance servent a publier les creneaux et gerer les capacites
  - les reservations servent a connaitre qui est inscrit sur chaque date
  - l'historique sert a comprendre, verifier et corriger les situations operationnelles
- **Access Scope**:
  - un adherent autorise accede a ses propres reservations et aux informations publiques de disponibilite des seances ouvertes
  - un administrateur accede a l'ensemble des seances, reservations, comptes et traces necessaires a l'exploitation
- **Retention / Deletion Approach**:
  - Les comptes actifs et les reservations a venir sont conserves tant qu'ils sont necessaires a l'exploitation courante.
  - L'historique des reservations et corrections est conserve au minimum pour la saison en cours et la saison precedente afin de permettre la reprise d'incident et l'explication des situations.
  - Au-dela de cette periode, les donnees historiques doivent pouvoir etre supprimees ou anonymisees si elles ne sont plus utiles a l'exploitation.

### Key Entities *(include if feature involves data)*

- **Compte utilisateur**: represente une personne autorisee a acceder a la web app avec une identite minimale, un email, un statut actif ou inactif et un role.
- **Seance reguliere**: represente une regle hebdomadaire servant a preparer des occurrences futures avec un jour, un horaire et une capacite par defaut.
- **Occurrence de seance**: represente une date concrete reservable avec un horaire, une capacite, un statut d'ouverture et un nombre de places restantes.
- **Reservation**: represente la prise d'une place par un adherent sur une occurrence de seance.
- **Trace d'audit**: represente une action horodatee sur une seance, une reservation ou un compte, avec l'acteur et le motif s'il est disponible.

### Assumptions

- La V1 couvre uniquement deux roles applicatifs: adherent autorise et administrateur.
- La gestion des coordinateurs, de la presence sur place et des regles de supervision reste hors application pour cette V1.
- Les comptes autorises existent ou peuvent etre prepares avant le lancement; l'import initial en masse n'est pas un objectif fonctionnel central de cette spec.
- Les adherents gerent leurs reservations pour des seances futures; aucune reservation sur une seance deja commencee n'est admise.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur smartphone, un adherent autorise peut se connecter, trouver une seance ouverte et reserver une place en moins de 2 minutes dans au moins 90 % des essais guides.
- **SC-002**: Un administrateur peut creer une seance ponctuelle ou modifier la capacite d'une seance existante en moins de 3 minutes sans assistance technique.
- **SC-003**: Aucune seance ne peut depasser sa capacite definie, y compris lorsque plusieurs adherents tentent de reserver les dernieres places.
- **SC-004**: 100 % des creations, reservations, annulations et corrections manuelles definies par cette spec sont consultables dans l'historique de la seance concernee.
- **SC-005**: Le fonctionnement nominal de la reservation reste possible sans dependance payante indispensable autre qu'un niveau de service compatible avec un budget associatif quasi nul.

# Feature Specification: Gestion des responsables de pratique libre

**Feature Branch**: `004-session-opener-management`  
**Created**: 2026-03-08  
**Status**: Draft  
**Input**: User description: "Ajouter un role responsable pour les pratiques libres. L admin accredite certains adherents comme responsables, cree et modifie les seances, et les seances de plus de 1h30 sont decoupees en creneaux de responsabilite de 90 minutes maximum. Les adherents s inscrivent sur un creneau; un responsable peut s y inscrire comme pratiquant ou prendre le role de responsable. Chaque creneau doit avoir exactement un responsable. A J-7, les responsables sont relances par email si un creneau n a pas de responsable. A J-2, seul le creneau sans responsable est annule et les inscrits concernes sont prevenus. Les emails partent depuis une adresse dediee visible par l admin, sans lecture des mails entrants."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prendre un creneau comme responsable depuis son telephone (Priority: P1)

Un adherent accredite comme responsable ouvre la web app sur son telephone, consulte les prochains creneaux de pratique libre qui n ont pas encore de responsable, puis se positionne comme responsable sur l un d eux. Il peut aussi choisir de rester simple pratiquant sur un creneau sans en prendre la responsabilite.

**Why this priority**: Le besoin coeur est de couvrir chaque creneau par exactement un responsable. Si ce parcours fonctionne, le club peut deja commencer a repartir les responsabilites sans attendre les automatismes email.

**Independent Test**: Avec des creneaux a venir deja crees par un administrateur, un responsable accredite peut se connecter sur smartphone, identifier un creneau sans responsable, prendre ce role, verifier que le creneau est maintenant couvert, puis renoncer a ce role pour remettre le creneau a decouvert.

**Acceptance Scenarios**:

1. **Given** un adherent accredite responsable est connecte sur smartphone et un creneau futur est sans responsable, **When** il prend le role de responsable sur ce creneau, **Then** le creneau affiche ce responsable comme unique responsable et n est plus signale comme non couvert.
2. **Given** un creneau futur a deja un responsable, **When** un second responsable accredite tente de prendre ce role, **Then** le systeme refuse l action et conserve le responsable deja affecte.
3. **Given** un adherent accredite responsable est inscrit comme pratiquant sur un creneau futur, **When** il prend ensuite le role de responsable sur ce meme creneau, **Then** son affectation comme responsable est enregistree sans supprimer son inscription pratiquant.

---

### User Story 2 - Preparer les seances et accrediter les responsables (Priority: P2)

Un administrateur gere les personnes autorisees a devenir responsables, cree ou modifie une seance de pratique libre, et voit le decoupage des creneaux associes. Si la seance dure plus de 1h30, elle est preparee avec plusieurs creneaux de responsabilite de 90 minutes maximum afin qu un responsable distinct puisse etre affecte a chacun.

**Why this priority**: Le flux responsable depend d une administration simple et explicite des droits, des seances et des creneaux. Sans cette base, le club ne peut ni preparer le planning ni reprendre la main manuellement.

**Independent Test**: Un administrateur accredite un adherent comme responsable, cree une seance longue, constate qu elle est decoupee en creneaux de 90 minutes maximum, puis corrige manuellement une affectation ou une accreditation depuis l interface web.

**Acceptance Scenarios**:

1. **Given** un adherent inscrit existe deja, **When** un administrateur lui attribue l accreditation responsable, **Then** cet adherent peut acceder aux actions de prise de responsabilite sans recevoir les droits d administration.
2. **Given** un administrateur cree une seance de 3 heures, **When** il enregistre cette seance, **Then** le systeme prepare automatiquement plusieurs creneaux successifs dont aucun ne depasse 1h30.
3. **Given** un administrateur retire l accreditation responsable a un utilisateur deja affecte sur de futurs creneaux, **When** il confirme cette modification, **Then** les futurs creneaux concernes redeviennent sans responsable et restent visibles comme a couvrir.

---

### User Story 3 - Relancer puis annuler automatiquement les creneaux non couverts (Priority: P3)

Le club veut un fonctionnement fiable sans suivi manuel quotidien. Les creneaux non couverts doivent donc etre signales a l avance aux responsables accredites, puis annules automatiquement assez tot pour prevenir les pratiquants deja inscrits sur le creneau concerne.

**Why this priority**: Les automatismes viennent apres le MVP manuel, mais ils reduisent fortement la charge operationnelle et evitent qu un creneau parte sans responsable connu.

**Independent Test**: Avec des creneaux futurs non couverts, on peut verifier qu un rappel est emis 7 jours avant aux responsables accredites, puis que le seul creneau encore non couvert est annule 2 jours avant et que les inscrits sur ce creneau recoivent la notification d annulation.

**Acceptance Scenarios**:

1. **Given** un creneau futur est a 7 jours de son debut et n a pas de responsable, **When** le rappel quotidien est traite, **Then** un email est envoye aux adherents accredites responsables pour signaler ce creneau non couvert.
2. **Given** un creneau futur est a 2 jours de son debut et n a toujours pas de responsable, **When** le traitement d echeance est execute, **Then** seul ce creneau est annule et les inscrits de ce creneau recoivent un email d information.
3. **Given** une seance contient plusieurs creneaux et un seul manque de responsable, **When** le traitement a J-2 s applique, **Then** les autres creneaux de la meme seance conservent leur statut initial et restent reservables ou maintenus selon leur propre etat.

### Edge Cases

- Une seance est creee moins de 7 jours avant son debut et certains creneaux sont deja sans responsable.
- Une seance est creee ou modifiee moins de 2 jours avant son debut avec un creneau non couvert.
- Un responsable abandonne son role sur un creneau apres le rappel a J-7 mais avant l echeance a J-2.
- Un administrateur retire l accreditation responsable d une personne deja affectee sur plusieurs creneaux futurs.
- Un adherent tente de s inscrire ou de prendre une responsabilite sur un creneau deja annule.
- Deux responsables accredites tentent presque en meme temps de prendre le meme creneau non couvert.
- Une seance longue est raccourcie ou allongee apres des inscriptions ou des affectations deja existantes.
- Un email automatique ne peut pas etre envoye: l administrateur doit quand meme pouvoir voir quels creneaux restent sans responsable et corriger manuellement.

## Requirements *(mandatory)*

### Roles & Rules

- **Actor Roles**:
  - `Adherent`: consulte les seances et creneaux futurs, s inscrit comme pratiquant sur un creneau et annule sa propre inscription tant que le creneau reste accessible.
  - `Responsable`: est d abord un adherent autorise par un administrateur a prendre la responsabilite d un creneau futur.
  - `Administrateur`: gere les comptes, attribue ou retire l accreditation responsable, cree et modifie les seances et creneaux, effectue des corrections manuelles, peut aussi agir lui-meme comme responsable.
- **Explicit Permissions**:
  - Un adherent non accredite responsable ne peut pas prendre la responsabilite d un creneau.
  - Un responsable n obtient aucun droit d administration supplementaire du seul fait de son accreditation.
  - Seul un administrateur peut creer, modifier, annuler ou corriger une seance ou un creneau, et attribuer ou retirer l accreditation responsable.
  - Un administrateur peut s affecter comme responsable sur un creneau s il choisit de couvrir lui-meme ce creneau.
  - Toute action non explicitement autorisee par cette spec ou par les specs precedentes reste interdite.
- **Resolved Business Rules**:
  - Une `seance` represente l evenement global de pratique libre.
  - Un `creneau responsable` represente un segment horodate de la seance sur lequel un adherent peut s inscrire et pour lequel exactement un responsable doit etre affecte.
  - Toute seance de plus de 1h30 est decoupee automatiquement en plusieurs creneaux successifs de 90 minutes maximum, avec un dernier creneau plus court si necessaire.
  - Les creneaux existent initialement sans responsable; l existence d un responsable n est pas une condition prealable a l ouverture des inscriptions.
  - L inscription comme pratiquant et l affectation comme responsable sont deux etats distincts sur un meme creneau.
  - Un creneau peut exister temporairement sans responsable tant qu il est a couvrir, mais il ne peut jamais avoir plus d un responsable a la fois et il doit etre soit couvert, soit annule au plus tard a J-2.
  - A J-7, tout creneau futur sans responsable declenche un rappel email aux responsables accredites.
  - A J-2, tout creneau futur encore sans responsable est annule individuellement; les autres creneaux de la meme seance ne sont pas annules par ricochet.
  - Les emails automatiques partent depuis une adresse applicative dediee visible par les administrateurs.
  - La lecture automatique des emails recus ne fait pas partie du perimetre.
- **Open Business Rules**:
  - Aucun point bloquant ouvert pour cette iteration.

### Functional Requirements

- **FR-001**: Le systeme MUST permettre a un administrateur d attribuer ou retirer l accreditation responsable a un adherent deja inscrit.
- **FR-002**: Le systeme MUST distinguer clairement les roles adherent, responsable et administrateur dans les permissions applicatives.
- **FR-003**: Le systeme MUST permettre a un administrateur de creer une seance avec au minimum une date, une heure de debut, une heure de fin et la capacite pratiquant de chaque creneau.
- **FR-004**: Le systeme MUST preparer automatiquement les creneaux responsables associes a une seance lors de sa creation ou de sa modification, en garantissant que chaque creneau dure 90 minutes maximum.
- **FR-005**: Le systeme MUST permettre a un administrateur de corriger manuellement le decoupage ou l etat d un creneau futur si une preparation automatique ne correspond plus au besoin reel.
- **FR-006**: Le systeme MUST afficher aux adherents sur smartphone les prochains creneaux avec au minimum leur horaire, leur statut d inscription et leur statut de couverture responsable.
- **FR-007**: Le systeme MUST permettre a un adherent de s inscrire comme pratiquant sur un creneau futur selon les regles de reservation deja definies pour la pratique libre.
- **FR-008**: Le systeme MUST permettre a un responsable accredite de prendre ou quitter le role de responsable sur un creneau futur tant que ce creneau n est pas annule ou deja commence.
- **FR-009**: Le systeme MUST empecher qu un creneau ait simultanement plus d un responsable affecte.
- **FR-010**: Le systeme MUST conserver separement l inscription pratiquant et l affectation responsable d une meme personne sur un meme creneau.
- **FR-011**: Le systeme MUST signaler explicitement lorsqu un creneau est sans responsable, couvert par un responsable ou annule.
- **FR-012**: Le systeme MUST permettre a un administrateur de voir pour chaque seance quels creneaux sont couverts, non couverts ou annules.
- **FR-013**: Le systeme MUST permettre a un administrateur d affecter ou de retirer manuellement un responsable sur un futur creneau pour reprise operationnelle.
- **FR-014**: Le systeme MUST rendre visibles aux administrateurs l adresse d envoi email appliquee par le systeme et le fait qu elle sert aux notifications automatiques.
- **FR-015**: Le systeme MUST emettre un rappel aux responsables accredites lorsqu un creneau futur atteint J-7 sans responsable affecte.
- **FR-016**: Le systeme MUST annuler automatiquement un creneau futur qui atteint J-2 sans responsable affecte.
- **FR-017**: Le systeme MUST informer les adherents inscrits sur un creneau annule de cette annulation et de l horaire concerne.
- **FR-018**: Le systeme MUST enregistrer une trace horodatee pour chaque attribution ou retrait d accreditation responsable.
- **FR-019**: Le systeme MUST enregistrer une trace horodatee pour chaque creation, modification, annulation ou correction manuelle de seance ou de creneau.
- **FR-020**: Le systeme MUST enregistrer une trace horodatee pour chaque prise ou abandon du role de responsable, pour chaque rappel J-7 emis et pour chaque annulation automatique J-2.
- **FR-021**: Le systeme MUST fournir a l administrateur une procedure manuelle de secours pour identifier les creneaux sans responsable et prevenir les inscrits meme si les emails automatiques ont echoue.
- **FR-022**: Le systeme MUST interdire la prise de role responsable ou l inscription pratiquant sur un creneau annule.
- **FR-023**: Le systeme MUST retirer l affectation responsable des futurs creneaux lorsqu un administrateur retire cette accreditation a une personne.
- **FR-024**: Le systeme MUST conserver la compatibilite avec les regles de reservation existantes de la pratique libre pour la capacite, les annulations adherent et les corrections manuelles d administration.

### Audit & Operations

- **Audit Events**:
  - attribution d une accreditation responsable
  - retrait d une accreditation responsable
  - creation d une seance
  - modification d une seance avec recalcul ou correction des creneaux
  - affectation d un responsable a un creneau
  - abandon ou retrait d une affectation responsable
  - inscription pratiquant ou annulation pratiquant sur un creneau
  - annulation manuelle d un creneau ou d une seance
  - rappel email emis a J-7 pour creneau non couvert
  - annulation automatique a J-2 pour creneau non couvert
  - notification d annulation envoyee aux inscrits concernes
- **Operational Procedure**:
  - L administrateur accredite d abord les adherents autorises a couvrir des creneaux comme responsables.
  - L administrateur cree ensuite les seances de pratique libre et controle le decoupage automatique des creneaux.
  - Les adherents et responsables s inscrivent ensuite sur les creneaux a venir; les responsables volontaires prennent le role de responsable sur les creneaux qu ils couvrent.
  - L administrateur suit les creneaux encore non couverts et corrige manuellement si besoin.
  - Les rappels et annulations automatiques reduisent ensuite le suivi manuel sur les echeances J-7 et J-2.
- **Manual Recovery**:
  - Si un creneau reste sans responsable, l administrateur peut affecter un responsable manuellement ou annuler lui-meme le creneau.
  - Si une affectation responsable est incorrecte, l administrateur retire ou remplace cette affectation depuis l interface d administration.
  - Si un email automatique n est pas parti, l administrateur s appuie sur la liste des creneaux non couverts, l historique et l adresse d envoi configuree pour relancer ou prevenir manuellement.
  - Si une seance est modifiee apres coup, l administrateur verifie que les inscriptions et responsabilites futures restent coherentes et ajuste les creneaux concernes.
- **Cost Impact**:
  - La fonctionnalite doit rester exploitable avec une adresse email applicative dediee et un hebergement compatibles avec un budget associatif nul ou quasi nul.

### Data & Privacy

- **Collected Data**:
  - role applicatif et statut d accreditation responsable des comptes
  - seances de pratique libre et creneaux associes
  - horaires, statut et capacite des creneaux
  - inscriptions pratiquant par creneau
  - affectations responsable par creneau
  - adresse email applicative de notification
  - historique des actions admin, responsable et systeme sur les seances et creneaux
- **Purpose of Each Data Item**:
  - le role et l accreditation determinent qui peut prendre une responsabilite
  - les seances et creneaux servent a publier et organiser la pratique libre
  - les horaires, statuts et capacites servent a savoir ce qui est maintenu, reservable ou annule
  - les inscriptions pratiquant servent a connaitre qui doit etre accueilli ou prevenu
  - les affectations responsable servent a garantir qu un responsable unique couvre chaque creneau
  - l adresse email applicative sert a identifier l expediteur des notifications automatiques
  - l historique sert a expliquer une situation, corriger un incident et prouver les decisions prises
- **Access Scope**:
  - un adherent voit les creneaux ouverts a son inscription et l etat de couverture responsable utile a sa comprehension du planning
  - un responsable voit en plus les actions lui permettant de prendre ou quitter une responsabilite
  - un administrateur accede a l ensemble des seances, creneaux, inscriptions, responsabilites, traces et adresse d envoi configuree
- **Retention / Deletion Approach**:
  - Les donnees a venir sont conservees tant qu elles sont necessaires a l exploitation courante.
  - Les traces d affectation responsable, de rappel, d annulation et de correction sont conservees au minimum pour la saison en cours et la saison precedente.
  - Au dela de cette periode, les donnees historiques doivent pouvoir etre supprimees ou anonymisees si elles ne sont plus utiles a l exploitation ou a la resolution d incidents.

### Key Entities *(include if feature involves data)*

- **Seance de pratique libre**: evenement parent defini par une date et un horaire global, pouvant contenir un ou plusieurs creneaux responsables.
- **Creneau responsable**: unite reservable rattachee a une seance, avec un horaire propre, une capacite pratiquant, un statut, zero ou un responsable actuel et potentiellement plusieurs traces d etat.
- **Affectation responsable**: association entre un compte accredite et un creneau, indiquant qui porte la responsabilite de ce creneau a un instant donne.
- **Inscription pratiquant**: participation d un adherent sur un creneau, distincte de toute responsabilite.
- **Notification operationnelle**: message emis par le systeme pour rappeler un creneau non couvert ou informer d une annulation de creneau.
- **Trace d audit**: enregistrement horodate d une action humaine ou automatique ayant un effet sur une accreditation, une seance, un creneau, une inscription ou une responsabilite.

### Assumptions

- Les regles de reservation pratiquant deja definies par la spec 001 continuent de s appliquer a chaque creneau reservable, sauf lorsqu un creneau est annule.
- Une seance longue est decoupee en creneaux successifs couvrant toute sa duree, par tranches de 90 minutes maximum, avec un dernier creneau plus court si besoin.
- Si un creneau est cree moins de 7 jours avant son debut et reste sans responsable, il apparait immediatement comme non couvert pour l administration; les automatismes d envoi suivent ensuite la prochaine echeance applicable.
- Si un creneau est cree ou devient non couvert moins de 2 jours avant son debut, l administrateur garde la possibilite de le corriger ou de l annuler manuellement sans attendre une intervention externe.
- L application n interprete pas les emails recus sur la boite dediee; elle se limite a l envoi des notifications sortantes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur smartphone, au moins 90 % des responsables accredites peuvent identifier un creneau non couvert et se positionner comme responsable en moins de 1 minute lors d un test guide.
- **SC-002**: Un administrateur peut accrediter un nouvel adherent comme responsable et verifier le resultat en moins de 2 minutes sans assistance technique.
- **SC-003**: 100 % des seances creees avec une duree superieure a 1h30 sont transformees en creneaux successifs dont aucun ne depasse 90 minutes.
- **SC-004**: 100 % des creneaux atteignant J-2 sans responsable sont annules individuellement et 100 % des adherents inscrits sur ces creneaux recoivent une information d annulation.
- **SC-005**: 100 % des actions definies par cette spec sur les accreditations, affectations responsable, rappels J-7, annulations J-2 et corrections manuelles sont consultables dans l historique d administration.
- **SC-006**: Le fonctionnement nominal de la fonctionnalite ne requiert aucun service payant supplementaire incompatible avec un budget associatif nul ou quasi nul.

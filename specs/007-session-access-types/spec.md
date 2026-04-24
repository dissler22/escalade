# Feature Specification: Droits d inscription par type de seance

**Feature Branch**: `007-session-access-types`  
**Created**: 2026-03-18  
**Status**: Draft  
**Input**: User description: "Ajouter des droits d inscription selon le profil utilisateur et le type de seance, en conservant trois parcours visibles: adherent, referent/prof et admin. Une pratique libre reste gerable avec couverture referent, un cours ajoute une logique d inscription par rattachement au cours et une edition limitee au prof sur ses propres occurrences."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - S inscrire seulement aux seances autorisees (Priority: P1)

Sur smartphone, un adherent consulte un calendrier unique qui melange pratiques libres et cours. En ouvrant le detail d une occurrence, il voit immediatement s il peut cliquer sur `S inscrire` selon son profil: pratique libre si son passport orange est actif, ou s il est referent/responsable, cours s il est rattache au cours concerne. Il doit rester maitre de chaque inscription, y compris pour les cours.

**Why this priority**: La valeur principale est d empecher les inscriptions non autorisees tout en laissant les adherents eligibles s inscrire simplement depuis le calendrier partage.

**Independent Test**: Avec trois adherents tests ayant des droits differents, chacun ouvre une pratique libre et une occurrence de cours depuis le calendrier. Les actions disponibles changent correctement selon le passport orange, l accreditation referent/responsable et les rattachements a des cours, sans inscription automatique.

**Acceptance Scenarios**:

1. **Given** un adherent avec un passport orange actif consulte une occurrence de pratique libre ouverte, **When** il ouvre le detail de cette occurrence, **Then** il voit l action `S inscrire` et peut finaliser son inscription.
2. **Given** un adherent rattache au cours `Escalade adultes` mais pas au cours `Competition`, **When** il ouvre le detail d une occurrence de chacun de ces cours, **Then** il peut s inscrire seulement a l occurrence du cours auquel il est rattache.
3. **Given** un adherent rattache a plusieurs cours, **When** il consulte plusieurs occurrences de cours sur la meme periode, **Then** il peut choisir de s inscrire separement a chaque occurrence autorisee.
4. **Given** un administrateur rattache un adherent a un cours, **When** l adherent revient sur le calendrier, **Then** il n est inscrit a aucune occurrence de ce cours tant qu il n a pas clique lui-meme sur `S inscrire`.

---

### User Story 2 - Operer selon le role referent ou prof (Priority: P2)

Un referent/responsable conserve le droit de s inscrire aux pratiques libres et d y gerer la couverture referent. Quand ce meme utilisateur est aussi prof sur un cours, il peut modifier uniquement les occurrences de ses propres cours, sans acceder a l administration globale ni aux series completes.

**Why this priority**: Ce flux definit la separation des pouvoirs la plus sensible du besoin: conserver des responsabilites metier utiles sans etendre les droits jusqu a l administration globale.

**Independent Test**: Avec un utilisateur cumule referent et prof, un testeur verifie qu il peut couvrir une pratique libre, modifier une occurrence d un cours qui lui est attribue et qu il ne peut ni modifier un autre cours ni changer une serie complete.

**Acceptance Scenarios**:

1. **Given** un referent/responsable consulte une pratique libre ouverte, **When** il ouvre son detail, **Then** il voit les actions d inscription et de couverture referent propres a cette pratique libre.
2. **Given** un prof est affecte au cours `Initiation`, **When** il ouvre une occurrence de ce cours en mode edition, **Then** il peut modifier cette occurrence uniquement.
3. **Given** ce meme prof consulte une occurrence d un autre cours ou la serie complete de `Initiation`, **When** il tente une modification, **Then** le systeme refuse l action et preserve les droits reserves a l administrateur.

---

### User Story 3 - Comprendre un calendrier mixte selon le type de seance (Priority: P3)

Un utilisateur connecte veut voir sur le meme calendrier les pratiques libres et les cours, y compris lorsqu ils tombent au meme moment. En selectionnant une occurrence, il obtient un detail adapte au type de seance: couverture referent pour une pratique libre, prof affiche sans logique de referent pour un cours.

**Why this priority**: Une fois les droits d inscription et d edition poses, il faut que la lecture du planning reste claire quand plusieurs types de seances coexistent et se chevauchent.

**Independent Test**: Sur une semaine contenant une pratique libre et un cours simultanes, un testeur ouvre successivement les deux occurrences. Il voit bien deux elements distincts et un panneau de detail qui change selon le type sans melanger les regles metier.

**Acceptance Scenarios**:

1. **Given** une pratique libre et un cours existent au meme jour et a la meme heure, **When** le calendrier de la semaine s affiche, **Then** les deux occurrences apparaissent comme deux elements distincts et selectionnables.
2. **Given** un utilisateur selectionne une pratique libre, **When** le detail s affiche, **Then** il voit les informations d inscription et de couverture referent sans information de prof de cours.
3. **Given** un utilisateur selectionne un cours, **When** le detail s affiche, **Then** il voit le prof associe et l action d inscription, sans logique de couverture referent.

### Edge Cases

- Un adherent cumule un passport orange, plusieurs rattachements a des cours et une accreditation referent: le detail de chaque occurrence ne doit montrer que les actions pertinentes pour son type.
- Une pratique libre et plusieurs cours se chevauchent exactement au meme moment: chaque occurrence doit rester distinguable et selectionnable depuis le calendrier.
- Un utilisateur perd son passport orange ou son rattachement a un cours apres s etre deja inscrit: les nouvelles inscriptions doivent etre bloquees et l administrateur doit pouvoir corriger manuellement l etat si necessaire.
- Un cours n a pas encore de prof renseigne au moment de l affichage: le detail du cours doit rester consultable et signaler l absence d affectation de prof sans activer de logique referent.
- Un prof est aussi referent/responsable: ses droits de couverture referent sur les pratiques libres ne doivent pas lui ouvrir de droits d edition sur d autres cours.
- Une occurrence est complete ou fermee: le calendrier peut rester visible, mais l action d inscription doit indiquer clairement qu elle n est pas disponible.

## Requirements *(mandatory)*

### Roles & Rules

- **Actor Roles**:
  - `Adherent`: consulte le calendrier partage et s inscrit uniquement aux occurrences autorisees par ses droits.
  - `Referent/responsable`: conserve les droits de l adherent, peut s inscrire aux pratiques libres et y gerer la couverture referent.
  - `Prof`: peut etre aussi referent/responsable et obtient un droit d edition limite a ses propres occurrences de cours.
  - `Administrateur`: cree tous les types de seances, gere les rattachements utilisateurs, les droits globaux et les corrections manuelles.
- **Explicit Permissions**:
  - Un adherent peut voir le calendrier mixte et ne peut s inscrire qu aux occurrences explicitement autorisees par son profil.
  - Un referent/responsable peut s inscrire aux pratiques libres meme sans passport orange et peut y gerer la couverture referent.
  - Un prof ne peut modifier que les occurrences des cours qui lui sont attribues; il ne peut ni modifier la serie complete, ni administrer d autres cours, ni acceder a l administration globale par ce seul statut.
  - Un administrateur conserve l administration globale de tous les utilisateurs, cours, pratiques libres et occurrences.
- **Resolved Business Rules**:
  - Le produit conserve trois parcours visibles: adherent, referent/prof et admin.
  - Le role admin reste le seul role d administration globale.
  - Le droit d inscription depend a la fois du profil utilisateur et du type d occurrence.
  - Une pratique libre est reservable par un utilisateur disposant d un passport orange actif ou d une accreditation referent/responsable.
  - Un cours est reservable seulement par un utilisateur rattache a ce cours.
  - Le rattachement a un cours n inscrit jamais automatiquement l utilisateur aux occurrences de ce cours.
  - Un utilisateur peut etre rattache a plusieurs cours en parallele et s inscrire separement a plusieurs occurrences de cours.
  - Le calendrier affiche ensemble pratiques libres et cours, y compris quand plusieurs occurrences existent au meme moment.
  - Le detail d une pratique libre affiche l inscription et la couverture referent.
  - Le detail d un cours affiche l inscription et le prof associe, sans logique de couverture referent.
  - Le droit d edition d un prof porte seulement sur les occurrences de ses propres cours.
- **Open Business Rules**:
  - Aucun point critique ouvert pour cette iteration.

### Functional Requirements

- **FR-001**: Le systeme MUST presenter un calendrier unique qui affiche les occurrences de pratique libre et de cours sur la meme periode consultee.
- **FR-002**: Le systeme MUST distinguer chaque occurrence comme un element selectionnable, y compris lorsque plusieurs occurrences existent au meme jour et a la meme heure.
- **FR-003**: Le systeme MUST identifier chaque occurrence comme etant soit une pratique libre, soit un cours, afin d adapter le detail et les actions disponibles.
- **FR-004**: Le systeme MUST autoriser l inscription a une occurrence de pratique libre seulement si l utilisateur a un passport orange actif ou une accreditation referent/responsable.
- **FR-005**: Le systeme MUST autoriser l inscription a une occurrence de cours seulement si l utilisateur est rattache au cours correspondant.
- **FR-006**: Le systeme MUST exiger une action explicite de l utilisateur pour l inscription a chaque occurrence de cours, meme apres un rattachement au cours par l administrateur.
- **FR-007**: Le systeme MUST permettre a un utilisateur d etre rattache a plusieurs cours et de gerer ses inscriptions occurrence par occurrence.
- **FR-008**: Le systeme MUST afficher une action d inscription seulement quand l occurrence est ouverte et autorisee pour l utilisateur connecte; sinon il MUST afficher un etat non disponible clair.
- **FR-009**: Le systeme MUST afficher dans le detail d une pratique libre les informations de reservation et la logique de couverture referent, sans afficher de logique propre aux cours.
- **FR-010**: Le systeme MUST afficher dans le detail d un cours les informations de reservation et le prof associe, sans afficher de logique de couverture referent.
- **FR-011**: Le systeme MUST permettre a l administrateur de creer et administrer globalement les pratiques libres, les cours, les occurrences, les passports orange, les rattachements aux cours et les affectations de prof.
- **FR-012**: Le systeme MUST permettre a un prof de modifier uniquement les occurrences des cours qui lui sont attribues.
- **FR-013**: Le systeme MUST interdire a un prof de modifier la serie complete d un cours, les occurrences d un autre prof ou toute configuration relevant de l administration globale.
- **FR-014**: Le systeme MUST conserver trois parcours visibles coherents avec le profil connecte: adherent, referent/prof et admin.
- **FR-015**: Le systeme MUST bloquer toute tentative d inscription ou d edition qui ne respecte pas les droits definis par le profil utilisateur et le type d occurrence.
- **FR-016**: Le systeme MUST enregistrer une trace exploitable pour chaque creation ou modification de droit d inscription, chaque inscription ou desinscription, chaque changement de couverture referent et chaque edition d occurrence de cours.
- **FR-017**: Le systeme MUST fournir a l administrateur un moyen de corriger manuellement un etat incoherent entre droits utilisateur, inscriptions et occurrences.

### Audit & Operations

- **Audit Events**:
  - activation, retrait ou modification d un passport orange
  - rattachement ou retrait d un utilisateur a un cours
  - affectation ou retrait d un prof sur un cours
  - creation et modification d une occurrence par un administrateur
  - modification d une occurrence de cours par le prof attribue
  - inscription et desinscription a une pratique libre
  - inscription et desinscription a un cours
  - prise ou abandon d une couverture referent sur une pratique libre
  - correction manuelle d un droit, d une inscription ou d une occurrence par un administrateur
- **Operational Procedure**:
  - L administrateur prepare les cours, pratiques libres, occurrences et droits utilisateurs.
  - L utilisateur connecte consulte le calendrier partage puis ouvre le detail de l occurrence voulue.
  - L utilisateur agit seulement sur les occurrences que son profil autorise.
  - Le prof attribue intervient uniquement pour corriger ou adapter ses propres occurrences de cours.
- **Manual Recovery**:
  - Si un utilisateur a perdu un droit apres une inscription deja effectuee, l administrateur revoit l occurrence concernee et corrige manuellement l inscription si necessaire.
  - Si une occurrence de cours a ete modifiee par erreur, l administrateur peut restaurer l etat attendu ou reappliquer la bonne affectation de prof.
  - Si une couverture referent devient incoherente sur une pratique libre, l administrateur corrige la couverture sans toucher a la logique des cours.
- **Cost Impact**:
  - Cette evolution ne doit introduire aucun cout recurrent obligatoire supplementaire au dela du fonctionnement courant du produit.

### Data & Privacy

- **Collected Data**:
  - statut de passport orange d un utilisateur
  - accreditation referent/responsable
  - rattachements d un utilisateur a un ou plusieurs cours
  - affectation d un prof a un cours
  - type de chaque occurrence de seance
  - inscriptions et desinscriptions par occurrence
  - couvertures referent pour les pratiques libres
  - traces de correction administrative
- **Purpose of Each Data Item**:
  - le passport orange et l accreditation referent/responsable servent a determiner l acces aux pratiques libres
  - les rattachements a des cours servent a determiner l acces aux occurrences de cours
  - l affectation de prof sert a afficher le prof du cours et a limiter les droits d edition
  - le type d occurrence sert a adapter l affichage du detail et les actions disponibles
  - les inscriptions, desinscriptions et couvertures referent servent a operer la participation aux seances
  - les traces de correction servent a verifier et retablir un etat metier correct
- **Access Scope**:
  - un adherent voit les occurrences du calendrier et les actions correspondant a ses droits
  - un referent/responsable voit en plus les actions de couverture des pratiques libres
  - un prof voit les occurrences de ses cours avec ses droits d edition limites a ces occurrences
  - un administrateur voit et corrige l ensemble des droits, occurrences et inscriptions
- **Retention / Deletion Approach**:
  - Cette spec n ajoute pas de nouvelle categorie de retention au dela des informations de seance, d inscription et de droits necessaires au fonctionnement du club.
  - Les droits, inscriptions, couvertures et traces d audit suivent les regles de retention deja appliquees aux donnees de gestion du club.

### Key Entities *(include if feature involves data)*

- **Profil d acces utilisateur**: ensemble des statuts qui pilotent les droits de l utilisateur, notamment son role visible, son passport orange, son accreditation referent/responsable et ses rattachements a des cours.
- **Cours**: activite a laquelle des adherents peuvent etre rattaches et a laquelle un prof peut etre affecte pour des occurrences donnees.
- **Occurrence de seance**: evenement reservable du calendrier, typifie comme pratique libre ou cours, avec ses inscriptions et son detail adapte.
- **Couverture referent**: engagement d un referent/responsable sur une pratique libre, distinct de la logique d un cours.
- **Inscription d occurrence**: decision explicite d un utilisateur de participer a une occurrence autorisee.

### Assumptions

- Le calendrier partage peut afficher une occurrence meme lorsqu un utilisateur n est pas autorise a s y inscrire; la difference se fait dans le detail et les actions disponibles.
- Les regles existantes de capacite, d ouverture, de fermeture et d annulation des occurrences restent inchangees et s appliquent apres le controle des droits de cette spec.
- Le detail d un cours affiche le prof actuellement affecte a l occurrence; en l absence d affectation, le detail signale simplement qu aucun prof n est renseigne.
- Les corrections manuelles de l administrateur restent exceptionnelles et servent de filet de securite, pas de parcours nominal.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Au moins 95 % des adherents eligibles guides peuvent ouvrir une occurrence depuis le calendrier et s y inscrire en moins de 90 secondes.
- **SC-002**: 100 % des tentatives d inscription non autorisees sont bloquees avec un etat clair indiquant pourquoi l action n est pas disponible.
- **SC-003**: 100 % des semaines contenant au moins deux occurrences simultanees affichent chaque occurrence comme un element distinct et selectionnable.
- **SC-004**: Au moins 90 % des profs guides peuvent modifier une occurrence de leur propre cours en moins de 2 minutes sans modifier une autre occurrence ni la serie complete.
- **SC-005**: 100 % des changements de droits d inscription, des inscriptions, desinscriptions, couvertures referent et editions d occurrences de cours sont retrouvables dans l historique d audit.
- **SC-006**: Cette evolution ne requiert aucun service payant supplementaire pour son fonctionnement nominal.

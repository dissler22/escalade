# Feature Specification: Rafraichissement visuel USMV

**Feature Branch**: `003-club-visual-refresh`  
**Created**: 2026-03-08  
**Status**: Draft  
**Input**: User description: "Ameliorer le visuel de l'application en s'inspirant du site actuel du club USM Viroflay Escalade pour rendre l'interface plus coherente avec l'identite visuelle du club, sans changer les fonctionnalites metier existantes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reconnaitre immediatement l'univers du club sur smartphone (Priority: P1)

Un adherent ouvre l'application sur son telephone pour reserver une seance. Des le premier ecran puis tout au long du parcours, il retrouve des reperes visuels clairement rattaches a l'USM Viroflay Escalade, ce qui rend l'application plus rassurante, plus lisible et plus professionnelle sans changer les actions deja connues.

**Why this priority**: La valeur principale de cette demande est de rendre l'application identifiable et coherente avec le club sur le parcours coeur mobile deja defini.

**Independent Test**: Depuis un smartphone, un adherent se connecte, consulte la liste des seances, ouvre une seance puis reserve ou annule sans reapprendre le produit. Il doit reconnaitre l'identite du club sur chaque ecran cle et retrouver les actions principales sans hesitation.

**Acceptance Scenarios**:

1. **Given** un adherent ouvre l'ecran de connexion sur smartphone, **When** il arrive sur l'application, **Then** il voit une presentation visuelle clairement rattachee au club et une hierarchie lisible des actions principales.
2. **Given** un adherent connecte consulte la liste des seances puis le detail d'une seance, **When** il navigue entre ces ecrans, **Then** la charte visuelle, la navigation et les etats d'action restent coherents d'un ecran a l'autre.
3. **Given** un adherent reserve puis annule une reservation sur une future seance, **When** il utilise les actions existantes, **Then** les libelles, les resultats et les regles metier restent inchanges malgre la mise a jour visuelle.

---

### User Story 2 - Utiliser des ecrans d'administration alignes avec le reste de l'application (Priority: P2)

Un administrateur gere les seances, les comptes et l'historique sur des ecrans qui reprennent la meme identite visuelle que les parcours adherent, avec une lisibilite suffisante pour des tableaux, formulaires et messages d'etat plus denses.

**Why this priority**: L'application ne doit pas donner l'impression de changer de produit entre la partie adherent et la partie administration. La coherence doit couvrir les ecrans les plus frequemment utilises par le club.

**Independent Test**: Un administrateur ouvre les listes, formulaires et historiques existants depuis un telephone puis un poste desktop. Il peut reperer rapidement les zones d'action, les informations prioritaires et les statuts sans perte de fonctionnalite.

**Acceptance Scenarios**:

1. **Given** un administrateur ouvre une liste de seances, de comptes ou d'historique, **When** il consulte l'ecran, **Then** la structure visuelle, les couleurs d'etat et les composants d'action sont coherents avec le reste de l'application.
2. **Given** un administrateur remplit un formulaire de creation ou de modification existant, **When** il saisit les champs et valide, **Then** la lisibilite et les retours visuels sont clairs sans changer les permissions ni les regles fonctionnelles.

---

### User Story 3 - Valider une refonte purement visuelle sans regression metier (Priority: P3)

Un responsable du produit ou un mainteneur verifie que la mise a jour renforce l'identite visuelle du club tout en preservant les parcours, droits et traces deja definis.

**Why this priority**: La demande est explicitement bornee a l'apparence. Il faut donc pouvoir prouver que les comportements metier existants n'ont pas ete modifies.

**Independent Test**: Un test de validation parcourt les ecrans coeur adherent et admin, puis rejoue les scenarios d'acceptation existants de reservation, d'annulation et d'administration. Les differences observees doivent etre uniquement visuelles ou ergonomiques.

**Acceptance Scenarios**:

1. **Given** la refonte visuelle est disponible en preproduction ou recette, **When** un responsable compare les ecrans cle a la reference visuelle du site public du club, **Then** il retrouve les marqueurs d'identite retenus et confirme que l'application reste reconnaissable comme un service USMV.
2. **Given** les parcours existants sont rejoues apres la refonte, **When** les utilisateurs effectuent les memes actions qu'avant, **Then** aucune regle metier, permission ou trace attendue n'est retiree ou alteree.

### Edge Cases

- Le logo ou un visuel de marque n'est pas disponible temporairement: l'application doit rester utilisable avec une presentation degradee mais toujours coherent.
- Un nom d'utilisateur, un titre de seance ou un message systeme est plus long que prevu: la mise en page doit rester lisible sur petit ecran sans masquer les actions principales.
- Un tableau d'administration comporte beaucoup de colonnes ou de lignes: l'information prioritaire et les actions frequentes doivent rester exploitables sur smartphone.
- Une seance est complete, fermee ou annulee: son etat doit rester clairement identifiable sans reposer uniquement sur la couleur.
- La connexion mobile est lente: les reperes visuels essentiels doivent apparaitre sans empecher l'acces rapide aux actions existantes.
- Un utilisateur non administrateur tente d'acceder a un ecran d'administration: la refonte ne doit pas affaiblir les separations de role deja en place.

## Requirements *(mandatory)*

### Roles & Rules

- **Actor Roles**:
  - `Adherent`: consulte les seances, reserve, annule et voit ses reservations dans une interface visuellement coherente avec le club.
  - `Administrateur`: gere les seances, les comptes et les historiques dans des ecrans alignes visuellement avec les parcours adherent.
  - `Responsable produit ou mainteneur`: valide la coherence avec l'identite visuelle du club et l'absence de regression metier.
- **Explicit Permissions**:
  - Un adherent voit uniquement les ecrans et actions deja prevus pour son role.
  - Un administrateur conserve les permissions existantes sur les ecrans d'administration.
  - Le responsable produit ou mainteneur peut verifier la conformite visuelle et fonctionnelle, sans que cette spec n'introduise de nouveaux droits applicatifs.
  - Toute action non explicitement autorisee par la spec 001 ou par les roles deja existants reste interdite.
- **Resolved Business Rules**:
  - Le perimetre couvre uniquement l'apparence, la hierarchie visuelle, la navigation perceptible et l'expression de l'identite de marque sur les ecrans existants.
  - Les parcours de connexion, reservation, annulation, administration, permissions et traces d'audit restent ceux deja definis par les specs existantes.
  - La reference visuelle doit reprendre les marqueurs les plus reconnaissables du site public actuel du club: contraste entre bleu fonce et bleu plus vif, fonds clairs, typographie plus institutionnelle pour les titres, typographie simple pour le texte courant, presence explicite du nom ou du sigle du club et presentation en blocs cartes ou panneaux lisibles.
  - Le parcours smartphone reste prioritaire sur tous les ecrans rafraichis.
  - La refonte peut reorganiser la presentation d'informations existantes pour ameliorer clarte et coherence, mais ne doit pas introduire de nouvelle fonctionnalite metier ni supprimer une action existante.
- **Open Business Rules**:
  - Aucun point bloquant ouvert pour cette iteration.

### Functional Requirements

- **FR-001**: Le systeme MUST afficher sur tous les ecrans coeur une identite visuelle commune clairement rattachee a l'USM Viroflay Escalade.
- **FR-002**: Le systeme MUST prioriser sur smartphone une lecture immediate du nom du club, du contexte de l'ecran et des actions principales.
- **FR-003**: Le systeme MUST appliquer une meme charte de presentation aux ecrans de connexion, liste des seances, detail de seance, reservations personnelles et ecrans d'administration existants.
- **FR-004**: Le systeme MUST conserver les memes parcours, permissions, libelles fonctionnels essentiels et consequences metier que ceux deja definis avant la refonte.
- **FR-005**: Le systeme MUST rendre visuellement distincts les etats importants tels que reservable, complet, ferme, annule, succes et erreur, sans s'appuyer uniquement sur la couleur.
- **FR-006**: Le systeme MUST fournir des composants visuellement coherents pour les boutons, liens, formulaires, messages, tableaux et cartes d'information sur l'ensemble des ecrans existants.
- **FR-007**: Le systeme MUST rendre les actions tactiles principales faciles a reperer et a activer sur petit ecran, y compris dans les formulaires et listes d'administration.
- **FR-008**: Le systeme MUST conserver une lisibilite correcte lorsque les contenus metier existants sont longs ou denses, notamment pour les noms, dates, messages et tableaux.
- **FR-009**: Le systeme MUST garder la navigation entre ecrans existants coherentement structuree pour qu'un utilisateur sache en permanence ou il se trouve et comment revenir a l'action precedente.
- **FR-010**: Le systeme MUST rester exploitable meme si certains elements decoratifs ou visuels de marque ne peuvent pas etre charges, en preservant la lisibilite et les actions coeur.
- **FR-011**: Le systeme MUST appliquer la meme logique de presentation aux messages de confirmation, d'erreur et d'information deja emis par l'application.
- **FR-012**: Le systeme MUST permettre une revue visuelle finie sur la liste complete des ecrans existants du MVP sans laisser d'ecran actif dans une presentation obsolete ou manifestement incoherente.

### Audit & Operations

- **Audit Events**:
  - Aucun nouvel evenement d'audit metier n'est cree par cette spec.
  - Tous les evenements d'audit deja requis par la spec 001 restent traces et consultables sans perte de lisibilite.
- **Operational Procedure**:
  - Le responsable produit ou le mainteneur recense les ecrans existants du MVP.
  - Il compare leur presentation a la reference visuelle retenue a partir du site public du club.
  - Il verifie ensuite les parcours adherent et admin pour confirmer que seuls l'habillage, la hierarchie visuelle et la navigation percue ont evolue.
- **Manual Recovery**:
  - Si un ecran rafraichi degrade la comprehension ou masque une action existante, le club doit pouvoir revenir temporairement a une presentation plus simple pour cet ecran sans bloquer le parcours metier.
  - Si un visuel de marque ne peut pas etre utilise, le service conserve une presentation sobre basee sur les couleurs, titres et libelles textuels deja approuves.
  - Si une incoherence visuelle est detectee apres mise a disposition, la correction prioritaire consiste a retablir la lisibilite et l'acces aux actions existantes avant toute finition esthetique.
- **Cost Impact**:
  - La refonte ne doit introduire aucun cout recurrent obligatoire au-dela de l'hebergement et des actifs visuels deja a disposition du club ou gerables a cout quasi nul.

### Data & Privacy

- **Collected Data**:
  - Aucun nouveau type de donnee personnelle n'est collecte par cette spec.
  - Les donnees metier existantes continuent d'etre affichees avec une presentation mise a jour.
  - Des actifs visuels non personnels du club peuvent etre exposes dans l'interface, comme le nom, le sigle, le logo ou des visuels deja publics.
- **Purpose of Each Data Item**:
  - Les donnees metier existantes conservent leur finalite actuelle.
  - Les actifs visuels de marque servent uniquement a renforcer l'identification du service et la coherence avec le club.
- **Access Scope**:
  - Les adherents et administrateurs accedent aux memes informations metier qu'avant selon leurs droits existants.
  - Les actifs visuels publics du club peuvent etre visibles sur les ecrans deja accessibles a ces roles.
- **Retention / Deletion Approach**:
  - Cette spec n'ajoute aucune nouvelle retention de donnees personnelles.
  - Les actifs visuels de marque sont conserves tant qu'ils restent approuves par le club et utiles a l'interface.

### Key Entities *(include if feature involves data)*

- **Reference visuelle du club**: ensemble des reperes approuves pour l'interface, comprenant palette, styles de titres, styles de texte, marqueurs de navigation et actifs de marque publics.
- **Ecran applicatif rafraichi**: une vue existante du produit dont la presentation est alignee avec la reference visuelle du club tout en conservant ses actions et informations metier.

### Assumptions

- Le site public actuel du club reste la source de reference visuelle principale pour cette iteration.
- Le logo, le nom du club et les marqueurs de marque deja publics peuvent etre reutilises dans l'application.
- La demande ne couvre ni refonte des regles de reservation ni ajout de contenus editoriaux nouveaux.
- Les ecrans existants du MVP a couvrir au minimum sont la connexion, les seances, les reservations personnelles et les ecrans d'administration deja presents dans le produit.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Sur smartphone, au moins 90 % des testeurs guides identifient l'application comme un service USMV Escalade en moins de 5 secondes sur l'ecran d'entree et sur au moins un ecran metier.
- **SC-002**: Au moins 90 % des testeurs deja familiers du produit retrouvent l'action principale attendue sur les ecrans coeur en moins de 10 secondes sans assistance supplementaire.
- **SC-003**: 100 % des ecrans actifs du MVP listes dans le perimetre de cette spec presentent la charte visuelle retenue sans rupture manifeste de navigation ou de composants.
- **SC-004**: 100 % des scenarios d'acceptation metier deja definis pour la reservation, l'annulation, l'administration et l'audit continuent de passer apres la refonte visuelle.
- **SC-005**: Le fonctionnement nominal de l'interface rafraichie ne requiert aucun service payant supplementaire au-dela du budget quasi nul deja accepte.

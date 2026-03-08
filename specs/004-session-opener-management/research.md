# Research: Gestion des responsables de pratique libre

## Decision: Conserver les roles existants `member/admin` et ajouter une accreditation responsable distincte

- **Rationale**: Le modele utilisateur actuel porte deja un champ `role` avec seulement `member` et `admin`. Ajouter une accreditation booleenne ou un statut dedie `is_responsable_accredited` permet de donner la capacite de couvrir un creneau sans ouvrir de droits d administration. Cela respecte la regle metier selon laquelle un admin peut aussi agir comme responsable, tout en gardant le controle d acces simple et explicite.
- **Alternatives considered**:
  - Ajouter un troisieme role enum `responsable`: rejete car cela melange permission d administration et capacite metier, et complique le cas `admin aussi responsable`.
  - Creer une table de roles generique many-to-many: rejete pour cette iteration car surdimensionne pour un seul nouveau privilege metier.

## Decision: Introduire une seance parent et des creneaux reservables enfants de 90 minutes maximum

- **Rationale**: La spec 004 distingue clairement la `seance` globale du `creneau` reservable. Le modele actuel `SessionOccurrence` represente aujourd hui l unite reservable. Pour respecter le besoin sans detruire la logique de reservations par unite, la conception retenue fait evoluer `SessionOccurrence` vers la seance parent datee, puis ajoute un modele enfant `SessionSlot` ou equivalent pour chaque creneau reservable avec capacite, statut et responsable. Les reservations et la responsabilite se placent sur le creneau enfant.
- **Alternatives considered**:
  - Conserver `SessionOccurrence` comme creneau et autoriser plusieurs occurrences le meme jour: rejete car la spec parle d une seance visible regroupant plusieurs creneaux et l unicite actuelle `(series, session_date)` deviendrait source de contournements.
  - Garder une seule occurrence reservable de plus de 90 minutes avec plusieurs responsables internes: rejete car contredit la regle d inscription sur un creneau et d annulation ciblee du seul creneau non couvert.

## Decision: Reutiliser la logique de reservation existante en la deplacant au niveau du creneau

- **Rationale**: Les services `bookings` gerent deja capacite, concurrence, annulation et audit avec verrouillage transactionnel. Le plus robuste est de conserver ces principes au niveau du creneau reservable enfant plutot que de reimplementer un moteur distinct. Cela preserve aussi la compatibilite avec la spec 001 sur capacite, annulation adherent et correction manuelle.
- **Alternatives considered**:
  - Laisser les reservations au niveau de la seance parent et suivre les responsables sur des sous-creneaux separes: rejete car impossible d annuler proprement le seul creneau non couvert et de prevenir uniquement les inscrits concernes.
  - Ajouter une table de presence parallele sans reutiliser `Reservation`: rejete car cela dupliquerait validations, etats et traces existants.

## Decision: Ajouter une affectation responsable explicite par creneau au lieu d une simple foreign key nue

- **Rationale**: Une table `ResponsibleAssignment` ou equivalent permet de tracer les prises et abandons de role dans le temps, d interdire proprement le double responsable actif et de garder l historique meme si l affectation change. Elle facilite aussi l audit et les corrections manuelles admin sans perdre le passe.
- **Alternatives considered**:
  - Un champ `responsible_user_id` directement sur le creneau: rejete car l historique de changements serait reporte uniquement dans l audit et moins exploitable pour les requetes metier.
  - Une simple colonne `current_responsible_id` avec table d historique separee plus tard: rejete pour cette feature car l audit des responsabilites fait partie du besoin coeur.

## Decision: Executer les echeances `J-7` et `J-2` via une commande Django planifiee sur la VM

- **Rationale**: La spec 002 cible une VM simple avec systemd et sans workers asynchrones ni service payant. Une commande Django idempotente, lancee quotidiennement par timer systemd ou cron, reste la solution la plus simple, peu couteuse et facile a reprendre manuellement. Elle couvre le rappel aux responsables accredites a J-7 et l annulation ciblee a J-2.
- **Alternatives considered**:
  - Ajouter Celery ou un scheduler applicatif resident: rejete pour cout, complexite et exploitation inutilement lourde.
  - Faire reposer les echeances uniquement sur des actions manuelles admin: rejete car la spec 004 demande explicitement des automatismes `J-7` et `J-2`.

## Decision: Configurer l email sortant hors code et exposer seulement l adresse d envoi en administration

- **Rationale**: Le site doit envoyer des emails depuis une adresse dediee visible par l admin, sans exposer les secrets. La configuration retenue est un expediteur applicatif en settings/env, un secret de connexion hors base et hors interface, et un ecran admin qui affiche l adresse d envoi active et l etat d activation de la notification.
- **Alternatives considered**:
  - Stocker le mot de passe SMTP en base et editable dans l interface: rejete pour des raisons evidentes de securite et de traçabilite.
  - Ne rien exposer en admin: rejete car la spec demande explicitement une adresse visible par l administrateur.

## Decision: Etendre l audit existant plutot que creer un journal parallele

- **Rationale**: `AuditEntry` couvre deja acteur, role capture, cible, motif, metadata et liens contextuels. L approche la plus simple est d y ajouter la reference de creneau enfant et de normaliser de nouveaux `action_type` pour accreditation responsable, affectation, retrait, rappel J-7, annulation J-2 et notification. On garde ainsi un historique unique consultable.
- **Alternatives considered**:
  - Journal dedie pour emails et responsabilites: rejete car le mainteneur et l admin devraient consulter plusieurs historiques pour comprendre un incident.
  - Metadonnees JSON seulement sans nouvelle relation: rejete car moins fiable pour filtrer l historique par creneau dans les ecrans admin.

## Decision: Considerer les memoires produit et test registry comme absentes et s aligner sur la constitution et les specs 001/002

- **Rationale**: Les fichiers `.specify/memory/product.md` et `.specify/memory/test-registry.md` ne sont pas presents dans ce repo. Pour eviter un plan base sur des hypotheses cachees, les contraintes autoritatives retenues sont la constitution, la spec 001 pour la reservation et la spec 002 pour l exploitation sur VM.
- **Alternatives considered**:
  - Bloquer le plan tant que ces fichiers n existent pas: rejete car l information necessaire est deja disponible dans les artefacts de reference existants.
  - Inventer un contenu implicite pour ces memoires: rejete car contraire a la discipline de spec.

# Research: Types de seance et droits d acces

## Decision 1: Reutiliser `SessionSeries` et `SessionOccurrence` comme socle unique

- **Decision**: Etendre les modeles existants de serie et d occurrence avec un type explicite `free_practice|course` plutot que creer deux familles de modeles separes.
- **Rationale**: Le produit gere deja des occurrences datees, un calendrier hebdomadaire et des reservations au niveau occurrence. Garder un backbone unique minimise les migrations, les routes et les surfaces de maintenance.
- **Alternatives considered**:
  - Creer un modele `Course` completement distinct des seances libres: rejete car cela dupliquerait calendrier, reservations, formulaires admin et historique.
  - Deriver le type de seance uniquement depuis le libelle ou la presence de creneaux: rejete car trop implicite et fragile pour les controles d acces.

## Decision 2: Modeliser les droits d inscription comme des attributs explicites, pas comme de nouveaux roles globaux

- **Decision**: Ajouter un passport orange explicite sur `User`, conserver l accreditation referent/responsable existante, et creer un rattachement explicite entre utilisateur et cours.
- **Rationale**: Le besoin distingue bien deux axes differents: les parcours visibles et les droits metier. Des relations explicites rendent les regles testables, auditables et simples a corriger par l admin.
- **Alternatives considered**:
  - Ajouter de nouveaux roles globaux `referent`, `prof`, `passport_orange`: rejete car un meme utilisateur peut cumuler plusieurs dimensions et les roles globaux ne couvrent pas bien les rattachements a plusieurs cours.
  - Encoder les rattachements a des cours dans un champ texte libre sur l utilisateur: rejete car non fiable pour les validations et l audit.

## Decision 3: Porter l appartenance a un cours sur une relation dediee et l ownership prof sur l occurrence

- **Decision**: Introduire une relation `CourseEnrollment` entre utilisateur et serie de type cours, et un `teacher_user` optionnel sur l occurrence de cours, initialise par defaut depuis la serie.
- **Rationale**: Le rattachement au cours est stable a l echelle de la serie, alors que le droit d edition demande par la spec vise uniquement les occurrences. Cette separation permet un MVP simple tout en laissant la possibilite d un remplacement ponctuel de prof sur une occurrence.
- **Alternatives considered**:
  - Assigner le prof uniquement a la serie: rejete car le detail utilisateur doit afficher le prof de l occurrence et une occurrence peut avoir besoin d un override ponctuel.
  - Assigner les rattachements utilisateur directement aux occurrences: rejete car la maintenance serait trop lourde pour l admin et contraire a la simplicite operationnelle.

## Decision 4: Conserver un calendrier membre unique avec detail conditionnel par type

- **Decision**: Reutiliser la vue hebdomadaire de la feature 006 et conditionner les actions et panneaux detail selon `session_type`.
- **Rationale**: Le besoin demande explicitement un calendrier unique. Le produit dispose deja d un view-model de calendrier; le faire evoluer est moins risque que separer la navigation en plusieurs pages.
- **Alternatives considered**:
  - Deux calendriers distincts, un pour les pratiques libres et un pour les cours: rejete car l utilisateur perdrait la vue d ensemble et la spec l exclut.
  - Un calendrier unique mais avec des regles d action decidees uniquement dans les templates: rejete car les controles d acces doivent rester centralises et testables dans les services.

## Decision 5: Limiter la logique de creneaux responsables aux pratiques libres

- **Decision**: Les occurrences de pratique libre conservent leurs `SessionSlot` et la couverture referent; les occurrences de cours n utilisent pas cette logique et n affichent pas de creneaux responsables.
- **Rationale**: La spec demande explicitement que le detail cours n embarque pas la logique referent. Isoler les creneaux responsables au type `free_practice` simplifie le calendrier, les validations et les tests.
- **Alternatives considered**:
  - Continuer a generer des creneaux pour tous les types et simplement masquer ceux des cours: rejete car cela maintiendrait une logique inutile et risquerait des effets de bord dans les services automatiques.
  - Remplacer entierement la logique de creneaux par une couverture au niveau occurrence: rejete car cela casserait le fonctionnement deja introduit pour les pratiques libres.

## Decision 6: Ajouter un parcours d edition prof dedie, distinct de l administration globale

- **Decision**: Introduire une route et un formulaire dedies a l edition d une occurrence de cours par son prof, avec un sous-ensemble de champs et des controles de permission explicites.
- **Rationale**: Le besoin autorise le prof a modifier seulement ses occurrences, pas a entrer dans l administration globale. Un parcours dedie est plus clair pour l utilisateur et plus sur qu une reutilisation directe des ecrans admin.
- **Alternatives considered**:
  - Ouvrir les URLs `/admin/sessions/...` aux profs avec des garde-fous supplementaires: rejete car cela melangerait les parcours visibles et augmenterait le risque de privilege creep.
  - Ne permettre aucune edition prof dans le MVP: rejete car cela manquerait un besoin metier explicite du perimetre.

## Decision 7: Garder les services de reservation et d audit existants, avec une nouvelle couche de politique d acces

- **Decision**: Conserver `bookings.services` et `audit.services` comme points d entree, en leur ajoutant une validation d eligibilite par type de seance et profil utilisateur.
- **Rationale**: Les validations nominales sur statut, date, capacite et audit existent deja. Ajouter une decision d acces en amont limite le risque de regression tout en rendant les nouveaux droits testables de maniere isolee.
- **Alternatives considered**:
  - Dupliquer les services de reservation pour les cours et les pratiques libres: rejete car cela multiplierait les chemins de code pour la meme action metier.
  - Faire le filtrage uniquement dans l interface: rejete car les controles de securite doivent rester appliques cote serveur.

## Residual Risks

- La migration du schema devra distinguer correctement les occurrences de cours et de pratique libre deja existantes si des donnees historiques sont reprises.
- L edition prof doit rester strictement bornee a un sous-ensemble de champs pour ne pas recreer une administration cachee.
- Les tests d integration devront couvrir les cumuls de droits, notamment un utilisateur a la fois referent, prof et rattache a plusieurs cours.

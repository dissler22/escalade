# Research: Vue calendaire hebdomadaire des seances

## Decision 1: Conserver un rendu serveur Django pour le calendrier hebdomadaire

- **Decision**: Generer la vue semaine directement depuis `sessions/views.py` et des templates Django existants, sans bibliotheque JavaScript de calendrier ni frontend separe.
- **Rationale**: Le repo est deja un monolithe a rendu serveur, la feature est avant tout une reorganisation de l information, et la constitution privilegie la simplicite operationnelle et le cout quasi nul.
- **Alternatives considered**:
  - Introduire une bibliotheque de calendrier cote navigateur: rejete car surdimensionne, plus couteux a maintenir et inutile pour un planning hebdomadaire simple.
  - Construire une petite API JSON puis une couche interactive front: rejete car cela dupliquerait la logique de presentation pour peu de valeur ajoutee.

## Decision 2: Utiliser des parametres de requete pour la semaine affichee et la seance selectionnee

- **Decision**: Faire porter l etat de navigation sur des parametres comme `week_start` et `selected_occurrence`, afin qu une meme route membre affiche la semaine voulue et le detail inline approprie.
- **Rationale**: Cela garde une URL partageable, simple a relire en cas d incident, compatible avec le rendu serveur et facile a reutiliser apres un POST.
- **Alternatives considered**:
  - Stocker la semaine selectionnee uniquement en session: rejete car moins transparent, moins testable et moins pratique pour les redirections apres action.
  - Creer une route distincte par semaine ou par seance: rejete car cela multiplie les routes sans gain fonctionnel reel.

## Decision 3: Faire de la page hebdomadaire la destination primaire et garder la fiche detail comme compatibilite

- **Decision**: La page calendrier hebdomadaire devient le parcours principal. L ancienne route de detail peut etre conservee comme compatibilite ou redirection vers la vue semaine avec selection prepositionnee.
- **Rationale**: La spec veut limiter les changements de page, mais garder une porte de repli reduit le risque de regression et facilite la transition des tests, liens internes et messages de redirection.
- **Alternatives considered**:
  - Supprimer immediatement toute route de detail: rejete car cela augmenterait le risque de rupture sur les liens existants et les flows de secours.
  - Conserver liste et detail separes en plus du calendrier: rejete car cela disperserait l usage et la maintenance.

## Decision 4: Reutiliser les actions POST existantes et rediriger vers la meme semaine

- **Decision**: Les actions de reservation, annulation, prise de responsabilite et abandon de responsabilite restent portees par les services et endpoints Django existants, avec une redirection vers la vue semaine et la seance selectionnee apres traitement.
- **Rationale**: Les services actuels portent deja les validations metier et l audit. Les reutiliser limite le risque sur un changement qui doit rester purement ergonomique.
- **Alternatives considered**:
  - Creer de nouveaux endpoints specifiques au calendrier: rejete car cela dupliquerait les validations et les traces pour une meme action.
  - Basculer les actions inline en JavaScript asynchrone des cette iteration: rejete car non necessaire pour satisfaire la spec.

## Decision 5: Introduire un modele de presentation dedie pour la grille semaine

- **Decision**: Construire en couche service des objets de presentation derives tels que semaine, colonnes de jours, blocs de seance et detail inline, sans changer le schema de base.
- **Rationale**: Le besoin porte sur l organisation visuelle de donnees existantes. Un view-model explicite isole les calculs de placement, de condensation et de selection, et garde les modeles metier sobres.
- **Alternatives considered**:
  - Enrichir directement les modeles Django avec toute la logique de placement calendrier: rejete car cela melangerait presentation et metier.
  - Calculer toute la structure uniquement dans le template: rejete car la logique deviendrait difficile a tester et a maintenir.

## Decision 6: Compacter la grille et reporter les textes longs dans un detail unique sous le calendrier

- **Decision**: Afficher dans la grille uniquement les informations decisives pour choisir une seance, puis afficher un detail complet unique sous la grille pour la seance selectionnee.
- **Rationale**: C est la reponse la plus directe a la demande de simplicite, de lisibilite et de reduction des changements de page. Cela reste coherent avec la refonte visuelle de la spec 003.
- **Alternatives considered**:
  - Garder des cartes detaillees dans chaque case du calendrier: rejete car trop dense sur smartphone.
  - Ouvrir un panneau detail par seance dans la grille: rejete car cela cree rapidement plusieurs zones ouvertes et degrade la lecture.

## Decision 7: Traiter les seances hors plage `8h-23h` par clipping visuel explicite

- **Decision**: La grille visible est bornee a `8h-23h`. Si une seance depasse cette plage, son bloc est affiche dans la partie visible avec une indication claire que l horaire reel deborde.
- **Rationale**: La spec impose cette plage horaire. Le clipping explicite permet de respecter le cadre sans masquer qu un evenement commence plus tot ou finit plus tard.
- **Alternatives considered**:
  - Etendre dynamiquement la grille selon les horaires reels: rejete car contraire a la regle de vue fixe de la spec.
  - Cacher purement et simplement la partie hors plage: rejete car cela tromperait l utilisateur sur la realite de la seance.

## Decision 8: Considerer les memoires produit et test registry comme absentes et s aligner sur les specs existantes

- **Decision**: Utiliser la constitution et les specs 001, 003 et 004 comme contraintes autoritatives pour cette planification, car `.specify/memory/product.md` et `.specify/memory/test-registry.md` ne sont pas presentes.
- **Rationale**: Ces documents couvrent deja le perimetre fonctionnel, la forme visuelle et les contraintes d exploitation necessaires a cette feature.
- **Alternatives considered**:
  - Bloquer la planification tant que ces memoires n existent pas: rejete car cela n apporte pas d information indispensable supplementaire.
  - Inventer des hypotheses de produit ou de registre de tests: rejete car contraire a la discipline de spec.

## Residual Risks

- Une grille hebdomadaire dense peut demander des arbitrages CSS fins pour rester lisible sur de petits ecrans.
- Les redirections apres POST devront conserver le contexte de semaine et de selection, sous peine de donner une impression de retour en arriere.
- Les tests existants fondes sur le texte `Voir la séance` devront etre adaptes au nouveau parcours principal.

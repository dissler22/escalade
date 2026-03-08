# Research: Rafraichissement visuel USMV

## Decision 1: Reprendre une palette et une hierarchie visuelle derivees du site public USMV, sans copier son theme complet

- **Decision**: Utiliser comme reference principale le bleu fonce institutionnel, le bleu plus vif d'accent, les fonds clairs et l'organisation en blocs lisibles observes sur le site public USMV Escalade, mais les transposer dans une charte plus legere adaptee a l'application de reservation.
- **Rationale**: Le site public expose deja les marqueurs les plus reconnaissables du club. Les reprendre permet d'augmenter immediatement la reconnaissance de marque, tout en evitant la surcharge d'un theme CMS plus large que les besoins de l'application.
- **Alternatives considered**:
  - Copier integralement le CSS public du club: rejete car trop couple a une structure HTML et a des dependances externes qui n'existent pas dans le monolithe Django.
  - Conserver le theme actuel en changeant seulement deux couleurs: rejete car insuffisant pour creer une vraie coherence entre ecrans adherent et admin.

## Decision 2: Garder un rendu serveur Django et concentrer la refonte dans `base.html`, les templates existants et la feuille `app.css`

- **Decision**: Conserver l'architecture actuelle a rendu serveur et faire la refonte via le shell HTML partage, les templates d'ecrans existants et une normalisation des composants visuels dans la feuille CSS existante.
- **Rationale**: Le produit a deja un nombre limite d'ecrans et un layout central. Modifier ces points de convergence maximise l'effet visuel avec un risque minimal sur les parcours et sans complexifier l'exploitation.
- **Alternatives considered**:
  - Introduire un framework frontend ou une bibliotheque de composants: rejete car hors besoin, plus couteux a maintenir et disproportionne pour une application associative.
  - Creer une seconde feuille de style specifique a certains ecrans: rejete car cela favoriserait des divergences de presentation entre parcours adherent et admin.

## Decision 3: Traiter la refonte comme un mini design system compose de tokens, composants partages et variantes d'ecrans

- **Decision**: Structurer la conception autour de trois niveaux: tokens de marque, composants reutilisables et patrons d'ecrans pour pages auth, membre et admin.
- **Rationale**: Cette approche limite les incoherences futures et fournit une base simple pour etendre la charte sans dupliquer des regles visuelles ecran par ecran.
- **Alternatives considered**:
  - Refaire chaque template independamment: rejete car cela augmente le risque de divergences et de regressions sur les futurs ecrans.
  - Miser uniquement sur des ajustements cosmetiques locaux: rejete car cela ne traite ni la navigation, ni la densite admin, ni les etats de messages.

## Decision 4: Faire porter la validation de la feature sur des pages HTML et des elements visibles, pas sur de nouveaux endpoints metier

- **Decision**: Documenter un contrat HTTP centre sur les pages et assets existants qui doivent afficher la nouvelle charte, plutot que d'introduire de nouveaux endpoints applicatifs.
- **Rationale**: La feature ne change pas le metier. Le contrat pertinent porte donc sur les surfaces UI a controler pendant la refonte et sur les actions HTTP deja en place.
- **Alternatives considered**:
  - Definir une nouvelle API dediee au theme: rejete car inutile et artificiel pour une application server-side.
  - Ne produire aucun contrat: rejete car le repo utilise deja un format OpenAPI comme artefact de reference et de controle.

## Decision 5: Imposer une accessibilite minimale par contraste, labels explicites et redondance des etats

- **Decision**: Exiger que les etats importants restent lisibles avec du texte, des libelles ou de la structure en plus de la couleur, et que les actions principales restent clairement identifiables sur petit ecran.
- **Rationale**: La spec impose deja que les etats ne reposent pas uniquement sur la couleur. Cette exigence est aussi necessaire pour conserver la comprehension lorsque le reseau est lent, que le visuel de marque manque ou que l'ecran admin est dense.
- **Alternatives considered**:
  - S'appuyer principalement sur un code couleur: rejete car contraire a la spec et fragile pour les usages reels.
  - Reporter ces sujets a une phase ulterieure: rejete car ils font partie du minimum de qualite attendu pour une refonte visuelle.

## Decision 6: Introduire un shell de navigation commun avec repere de role explicite

- **Decision**: Ajouter un header partage mettant en avant le nom du club, un repere de role (`adherent` ou `administrateur`) et une navigation uniforme.
- **Rationale**: Cela cree une continuite immediate entre connexion, parcours membre et ecrans admin sans toucher aux routes ni aux permissions.
- **Alternatives considered**:
  - Refaire chaque page sans shell commun: rejete car cela aurait maintenu des ruptures visuelles.
  - Limiter la marque au seul ecran de connexion: rejete car la coherence devait couvrir tout le parcours.

## Decision 7: Preferer des tableaux empilables mobile et une timeline pour l'audit

- **Decision**: Conserver les tableaux pour les vues denses, mais les rendre lisibles sur petit ecran via un affichage empile; presenter l'audit sous forme de cartes chronologiques.
- **Rationale**: Les besoins admin restent denses. Une refonte purement visuelle doit donc ameliorer la lecture mobile sans changer le fond des donnees affichees.
- **Alternatives considered**:
  - Remplacer tous les tableaux par des cartes dediees: rejete car cela alourdissait les edits et diminuait la densite utile sur desktop.
  - Laisser les tableaux bruts en scroll horizontal: rejete car moins lisible sur smartphone.

## Residual Risks

- Sans revue sur de vrais telephones, certaines longueurs de texte peuvent encore produire des retours a la ligne peu elegants.
- Les formulaires admin restent rendus via `form.as_p`; la coherence repose donc fortement sur la feuille CSS commune.
- L'absence d'actif graphique officiel impose une marque textuelle forte; si un logo valide est fourni plus tard, il pourra etre ajoute sans changer les parcours.

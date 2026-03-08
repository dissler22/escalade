# Data Model: Rafraichissement visuel USMV

## Overview

Cette feature n'introduit aucun changement de schema persistant dans la base applicative. Le modele ci-dessous decrit les entites conceptuelles de presentation necessaires pour concevoir, implementer et valider la refonte visuelle sur les ecrans HTML existants.

## Entity: VisualTheme

- **Purpose**: Definir la charte de presentation commune a tous les ecrans actifs du produit.
- **Fields**:
  - `theme_id`: identifiant logique de la charte active.
  - `brand_name`: nom ou sigle du club affiche dans l'interface.
  - `primary_color`: couleur institutionnelle dominante.
  - `accent_color`: couleur d'action ou de mise en avant.
  - `surface_palette`: ensemble de fonds et panneaux clairs.
  - `text_palette`: couleurs de texte principal, secondaire et inverse.
  - `status_palette`: styles reserves aux etats succes, erreur, complet, ferme, annule.
  - `heading_style`: style des titres principaux et secondaires.
  - `body_style`: style du texte courant et des meta-informations.
  - `spacing_scale`: rythme d'espacement de reference.
  - `focus_style`: indicateur de focus et d'action clavier ou tactile.
- **Validation Rules**:
  - Les couleurs d'etat critiques doivent rester distinguables sans reposer uniquement sur la couleur.
  - Le theme doit fonctionner avec ou sans actif graphique optionnel.
  - Les styles doivent rester lisibles sur smartphone.

## Entity: BrandAssetReference

- **Purpose**: Representer les actifs visuels publics du club utilises dans l'application.
- **Fields**:
  - `asset_type`: logo, sigle, nom developpe, icone ou visuel decoratif.
  - `display_priority`: niveau de priorite dans l'interface.
  - `usage_scope`: pages ou zones ou l'actif peut etre affiche.
  - `fallback_text`: texte a afficher si l'actif est absent.
  - `is_optional`: indique si l'ecran reste completement utilisable sans cet actif.
- **Validation Rules**:
  - Tout actif doit avoir un fallback textuel.
  - Aucun actif ne doit masquer une action metier essentielle.

## Entity: NavigationFrame

- **Purpose**: Definir le shell partage par les ecrans de l'application.
- **Fields**:
  - `frame_type`: authentification, adherent ou administration.
  - `brand_zone`: zone de marque visible en tete.
  - `context_label`: libelle indiquant l'ecran ou le role courant.
  - `primary_navigation`: liens principaux visibles selon le role.
  - `message_zone`: emplacement des messages de succes ou d'erreur.
  - `content_container`: largeur, marges et structure du contenu central.
- **Validation Rules**:
  - Le cadre de navigation doit rester coherent entre ecrans d'un meme role.
  - Les actions principales doivent etre visibles sans recherche excessive sur smartphone.

## Entity: UIComponent

- **Purpose**: Formaliser les composants visuels reutilisables.
- **Fields**:
  - `component_name`: bouton, lien d'action, badge, carte, formulaire, tableau, message, groupe d'actions.
  - `variant`: primaire, secondaire, danger, information, neutre.
  - `states`: repos, hover, focus, actif, desactive, indisponible.
  - `density_mode`: compact, standard ou dense.
  - `mobile_behavior`: empilement, debordement gere, largeur pleine, alignement prioritaire.
  - `semantic_usage`: contexte metier permis pour ce composant.
- **Validation Rules**:
  - Une variante ne doit pas changer le sens metier de l'action.
  - Les etats doivent rester comprehensibles sur petit ecran.
  - Les composants admin denses doivent conserver la lisibilite des informations prioritaires.

## Entity: ScreenVariant

- **Purpose**: Decrire les ecrans existants qui doivent adopter la charte.
- **Fields**:
  - `screen_id`: identifiant logique de l'ecran.
  - `route_pattern`: route HTTP existante associee.
  - `role_scope`: public authentifie, adherent ou administrateur.
  - `content_priority`: ordre de lecture souhaite sur smartphone.
  - `primary_action`: action principale a rendre evidente.
  - `secondary_actions`: actions utilitaires autorisees.
  - `data_density`: faible, moyenne ou forte.
  - `status_signals`: etats metier visibles sur l'ecran.
- **Relationships**:
  - Chaque `ScreenVariant` utilise un `NavigationFrame`.
  - Chaque `ScreenVariant` applique un `VisualTheme`.
  - Chaque `ScreenVariant` consomme plusieurs `UIComponent`.
- **Validation Rules**:
  - L'action principale doit rester visible dans les 10 premieres secondes de lecture sur smartphone.
  - Aucun ecran actif du MVP ne doit rester dans un ancien style incoherent.

## Screen to Component Mapping

| ScreenVariant | NavigationFrame | UIComponent obligatoires | Action principale |
|---------------|-----------------|--------------------------|-------------------|
| `login` | `authentication` | `brand-zone`, `form-panel`, `primary-button`, `info-card`, `flash-message` | authentifier le compte |
| `member-session-list` | `member` | `hero-panel`, `status-badge`, `session-card`, `secondary-link`, `flash-message` | ouvrir une fiche seance |
| `member-session-detail` | `member` | `hero-panel`, `status-badge`, `stat-card`, `primary-button`, `secondary-button` | reserver ou annuler |
| `member-bookings` | `member` | `hero-panel`, `reservation-card`, `status-badge`, `secondary-button`, `empty-state` | annuler une reservation |
| `admin-session-dashboard` | `administration` | `hero-panel`, `action-group`, `responsive-table`, `status-badge`, `ghost-button` | creer ou editer une seance |
| `admin-series-form` | `administration` | `hero-panel`, `form-panel`, `primary-button`, `secondary-button` | enregistrer une serie |
| `admin-occurrence-form` | `administration` | `hero-panel`, `form-panel`, `status-control`, `primary-button`, `secondary-button` | enregistrer ou changer un statut |
| `admin-session-reservations` | `administration` | `hero-panel`, `metric-pill`, `form-panel`, `responsive-table`, `danger-button` | ajouter ou retirer une reservation |
| `admin-account-list` | `administration` | `hero-panel`, `responsive-table`, `role-badge`, `inline-form`, `secondary-button` | mettre a jour un compte |
| `admin-audit-history` | `administration` | `hero-panel`, `timeline-card`, `status-badge`, `empty-state` | verifier une trace |

## Entity: VisualReviewChecklist

- **Purpose**: Encadrer la validation manuelle de la refonte.
- **Fields**:
  - `review_scope`: liste des ecrans a controler.
  - `brand_recognition_check`: verification de la reconnaissance USMV.
  - `mobile_legibility_check`: verification de lisibilite sur petit ecran.
  - `admin_density_check`: verification des listes, formulaires et tableaux admin.
  - `status_visibility_check`: verification des etats et messages.
  - `business_regression_check`: confirmation que les parcours et permissions sont inchanges.
- **Validation Rules**:
  - La revue doit couvrir au minimum connexion, liste des seances, detail, reservations personnelles et ecrans admin actifs.
  - Toute anomalie critique bloque la validation tant qu'une action centrale est masquee ou ambigue.

## State Notes

- `BrandAssetReference` peut etre en etat logique `available` ou `missing`; dans les deux cas, l'application doit rester exploitable.
- `UIComponent` peut etre en etat logique `legacy`, `refreshed` ou `degraded fallback` pendant la migration ecran par ecran.
- Aucun etat de cette feature ne modifie les statuts metier existants de `SessionOccurrence`, `Reservation` ou `AuditEntry`.

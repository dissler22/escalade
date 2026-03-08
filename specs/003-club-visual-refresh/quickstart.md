# Quickstart: Rafraichissement visuel USMV

## Goal

Verifier localement que la refonte visuelle rend l'application reconnaissable comme un service USMV Escalade sans changer les comportements metier existants.

## Prerequisites

- Python 3.12+ disponible localement
- Dependances du projet installees
- Base locale initialisee
- Au moins un compte adherent et un compte administrateur disponibles pour revue

## Local Run

```bash
cd /home/marius/work/repos/escalade
python -m pip install -e .[dev]
python src/manage.py migrate
python src/manage.py runserver
```

L'application est ensuite disponible sur `http://127.0.0.1:8000`.

## Visual Review Flow

1. Ouvrir `http://127.0.0.1:8000/login/` sur un viewport smartphone.
2. Verifier la presence immediate de l'identite USMV, la lisibilite du formulaire et la clarte de l'action principale.
3. Se connecter avec un compte adherent.
4. Parcourir:
   - `/sessions/`
   - `/sessions/<occurrence_id>/`
   - `/bookings/mine/`
5. Confirmer que la navigation, les messages, les badges d'etat et les boutons sont coherents d'un ecran a l'autre.
6. Se connecter avec un compte administrateur.
7. Parcourir:
   - `/admin/sessions/`
   - `/admin/sessions/series/new/`
   - `/admin/sessions/occurrences/new/`
   - `/admin/bookings/sessions/<occurrence_id>/`
   - `/admin/accounts/`
   - `/admin/audit/sessions/<occurrence_id>/`
8. Verifier que les ecrans admin restent lisibles malgre une densite plus forte et que les actions frequentes restent evidentes.
9. Rejouer un scenario metier existant:
   - connexion adherent
   - consultation d'une seance
   - reservation ou annulation
   - verification du message resultat
10. Confirmer qu'aucune permission, route ou consequence metier n'a change.

## Review Matrix

| Ecran | Role | Reperes a controler | Action principale a retrouver |
|-------|------|---------------------|-------------------------------|
| `/login/` | invite | nom du club, contraste du formulaire, lisibilite des champs | se connecter |
| `/sessions/` | adherent | hero de page, badges d'etat, cartes lisibles, navigation | voir une seance |
| `/sessions/<occurrence_id>/` | adherent | statut, capacite, bouton principal, retour de navigation | reserver ou annuler |
| `/bookings/mine/` | adherent | cartes de reservation, bouton d'annulation, continuites de style | annuler une reservation |
| `/admin/sessions/` | administrateur | reperes admin, tables empilables mobile, acces rapides | creer, editer, ouvrir audit |
| `/admin/sessions/series/new/` | administrateur | hierarchie formulaire, boutons partages | enregistrer une serie |
| `/admin/sessions/occurrences/new/` | administrateur | densite formulaire, bloc statut, lisibilite des champs | enregistrer une seance |
| `/admin/bookings/sessions/<occurrence_id>/` | administrateur | capacite restante, ajout manuel, table d'inscrits | ajouter ou retirer un inscrit |
| `/admin/accounts/` | administrateur | badges role/activation, controles inline, table responsive | mettre a jour un compte |
| `/admin/audit/sessions/<occurrence_id>/` | administrateur | timeline lisible, statut d'evenement, acteur et motif | verifier une trace |

## Review Checklist

- L'application est identifiable comme un service USMV en moins de 5 secondes.
- L'action principale de chaque ecran coeur est identifiable en moins de 10 secondes.
- Les etats `ouvert`, `complet`, `ferme`, `annule`, `succes` et `erreur` restent explicites sans reposer uniquement sur la couleur.
- Les tableaux et formulaires admin restent exploitables sur petit ecran.
- Les messages flash, liens de navigation et boutons utilisent une meme logique visuelle.
- En absence d'un actif visuel optionnel, le texte et la structure restent suffisants pour utiliser l'application.

## Smartphone Criteria

- Zone de marque visible sans scroller sur les ecrans coeur.
- Action principale exploitable au pouce sans zoom horizontal.
- Statuts critiques visibles en texte, pas seulement par la couleur.
- Tableaux admin comprenables sous forme empilee si la largeur est contrainte.
- Retour au contexte precedent disponible en un geste ou un lien evident.

## Regression Focus

- Connexion et deconnexion
- Liste des seances
- Detail d'une seance
- Reservation et annulation adherent
- Creation ou edition admin de seance
- Consultation des reservations admin
- Consultation de l'historique d'audit

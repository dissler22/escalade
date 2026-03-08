# Quickstart: Vue calendaire hebdomadaire des seances

## Goal

Verifier rapidement que le parcours membre des seances se fait depuis une vue hebdomadaire unique, lisible sur smartphone, avec detail inline et sans changement de page inutile.

## Preconditions

- Branche courante: `006-session-calendar`
- Environnement virtuel du repo disponible
- Base locale initialisee
- Au moins trois comptes de test:
  - un `member`
  - un `member` deja reserve sur une seance ouverte
  - un `responsable accredite`
- Au moins une semaine de test contenant:
  - plusieurs seances ouvertes
  - au moins une seance complete ou fermee
  - au moins une seance avec creneau sans responsable

## Local validation flow

1. Lancer les migrations et le serveur local.
2. Ouvrir `/sessions/` sur un viewport smartphone.
3. Verifier que l ecran principal affiche:
   - une semaine complete, meme si elle peut etre vide
   - une echelle horaire `8h-23h`
   - des blocs de seances courts et lisibles
4. Verifier la navigation de semaine:
   - semaine suivante
   - semaine precedente
   - conservation d une URL explicite avec contexte de semaine
5. Taper une seance dans la grille et verifier que:
   - le detail apparait sous le calendrier
   - aucun changement de page n est necessaire
   - une seule seance detaillee est visible a la fois
6. Depuis le detail inline avec un compte membre:
   - reserver une seance ouverte
   - verifier le message de succes
   - verifier que le retour reste sur la meme semaine et la meme seance
   - annuler ensuite la reservation depuis la meme page
7. Depuis le detail inline avec un compte responsable accredite:
   - prendre un creneau non couvert
   - verifier le message de succes
   - abandonner ensuite la responsabilite
8. Verifier les cas limites visibles:
   - semaine vide
   - seance complete
   - seance annulee ou non reservable
   - titre long dans la grille
9. Ouvrir directement l ancienne URL de detail d une seance et verifier qu elle renvoie vers le parcours semaine ou qu elle offre un repli compatible documente.
   - verifier que la redirection revient sur la bonne semaine et au detail inline de la bonne seance
10. Depuis l administration, verifier qu une reservation ou une responsabilite declenchee depuis la vue calendrier est bien visible dans les ecrans de suivi existants.

## Suggested verification commands

```bash
cd /home/marius/work/repos/escalade
.venv/bin/python src/manage.py migrate
.venv/bin/python src/manage.py runserver
pytest
```

## Test Focus

- `tests/unit/`
  - calcul du debut de semaine et de la plage visible `8h-23h`
  - construction des blocs de calendrier et clipping hors plage
  - selection par defaut de la seance detaillee
  - preservation du contexte de retour apres action
- `tests/integration/`
  - affichage de la page `/sessions/` en vue semaine
  - navigation semaine precedente et suivante
  - detail inline sur la meme page
  - reservation, annulation et responsabilite sans passage obligatoire par une fiche separee
  - compatibilite de l ancienne route de detail
- `tests/contract/`
  - parametres `week_start` et `selected_occurrence`
  - presence du contrat de detail inline
  - redirections POST vers la vue semaine
- `tests/e2e/`
  - validation tactile sur viewport mobile si cette couche est active dans l equipe

## Manual Recovery Drill

1. Forcer une erreur metier connue, par exemple une seance devenue complete entre affichage et soumission.
2. Rejouer l action depuis la vue semaine.
3. Verifier que le message d erreur apparait sans perdre le contexte de semaine ni la seance selectionnee.
4. Ouvrir ensuite l administration pour controler l etat reel de la seance.
5. Corriger manuellement si necessaire depuis les ecrans admin existants.

## Daily Manual Recovery

1. Ouvrir `/sessions/` et verifier la semaine en cours sur smartphone.
2. Si un adherent signale un comportement incoherent, retrouver la seance concernee via la semaine ou via l URL de compatibilite.
3. Controler ensuite l etat source dans les ecrans d administration existants.
4. Corriger la reservation ou la responsabilite si besoin depuis l administration, sans dependre d un outil externe.

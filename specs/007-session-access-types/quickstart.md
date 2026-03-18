# Quickstart: Types de seance et droits d acces

## Goal

Verifier rapidement que le produit gere un calendrier mixte `pratique libre + cours`, applique les droits d inscription selon le profil utilisateur, et permet a un prof de modifier seulement les occurrences de ses propres cours.

## Preconditions

- Branche courante: `007-session-access-types`
- Environnement virtuel du repo disponible
- Base locale initialisee
- Au moins cinq comptes de test:
  - un `admin`
  - un `member` sans passport orange ni cours
  - un `member` avec passport orange
  - un `member` rattache a au moins deux cours
  - un utilisateur `member` accredite responsable et affecte prof sur un cours
- Au moins une semaine de test contenant:
  - une pratique libre ouverte avec creneaux responsables
  - un cours ouvert avec prof assigne
  - un cours sans prof assigne
  - au moins une pratique libre et un cours au meme moment

## Local validation flow

1. Lancer les migrations et le serveur local.
2. Connecte en admin, ouvrir `/admin/accounts/` puis verifier qu il est possible de:
   - activer ou retirer le passport orange
   - conserver ou retirer l accreditation responsable
   - rattacher un adherent a un ou plusieurs cours
3. Toujours en admin, ouvrir `/admin/sessions/` puis verifier qu il est possible de:
   - creer une occurrence ou une serie de type `pratique libre`
   - creer une occurrence ou une serie de type `cours`
   - affecter un prof a un cours
4. Connecte en adherent sans droits speciaux, ouvrir `/sessions/` sur un viewport smartphone:
   - verifier que le calendrier affiche pratiques libres et cours dans la meme semaine
   - verifier qu une occurrence libre non autorisee et un cours non rattache restent visibles mais non reservables
5. Avec le compte membre disposant d un passport orange:
   - ouvrir une pratique libre
   - verifier que `S inscrire` est disponible
   - effectuer l inscription puis la desinscription
6. Avec le compte rattache a plusieurs cours:
   - ouvrir successivement deux occurrences de cours autorisees
   - verifier que `S inscrire` reste une action manuelle sur chaque occurrence
   - verifier qu aucun rattachement n a cree d inscription automatique
7. Avec le compte referent/prof:
   - ouvrir une pratique libre et verifier la presence des actions de couverture referent
   - ouvrir une occurrence de son propre cours et verifier la presence d une action d edition occurrence-only
   - verifier qu une occurrence d un autre cours ne propose pas cette edition
8. Depuis l ecran d edition prof:
   - modifier une occurrence de son cours
   - enregistrer
   - verifier que la mise a jour est visible sur le calendrier et dans l audit
9. Depuis l administration ou l audit:
   - verifier les evenements de changement de passport orange
   - verifier les evenements de rattachement a un cours
   - verifier les evenements d inscription/desinscription et d edition prof

## Suggested verification commands

```bash
cd /home/marius/work/repos/escalade
.venv/bin/python src/manage.py migrate
.venv/bin/python src/manage.py runserver
pytest
```

## Test Focus

- `tests/unit/`
  - politique d acces par type de seance
  - eligibility pratique libre via passport orange ou accreditation responsable
  - eligibility cours via `CourseEnrollment`
  - autorisation d edition prof uniquement sur ses occurrences de cours
- `tests/integration/`
  - calendrier mixte avec occurrences simultanees
  - masquage et affichage conditionnel des actions dans le detail
  - administration des passports orange, rattachements cours et affectations prof
  - edition occurrence-only par le prof
- `tests/contract/`
  - contrats des pages calendrier, administration des droits et edition prof
  - reponses de refus `403` ou `409` sur tentative non autorisee
- `tests/e2e/`
  - verification mobile de la navigation mixte si la couche existe dans l equipe

## Manual Recovery Drill

1. Retirer un rattachement a un cours apres qu un adherent s y est deja inscrit.
2. Rejouer une tentative d inscription sur une autre occurrence de ce cours.
3. Verifier que l action est maintenant refusee avec un message clair.
4. Ouvrir `/admin/accounts/` puis `/admin/bookings/` pour controler l etat reel.
5. Corriger manuellement l inscription ou le rattachement si la situation du club l exige.

## Daily Manual Recovery

1. Si un utilisateur remonte un probleme de droit d inscription, verifier d abord son passport orange, son accreditation responsable et ses rattachements cours dans l administration.
2. Verifier ensuite l occurrence concernee dans `/admin/sessions/`.
3. Corriger manuellement le droit, l affectation prof ou l inscription si besoin.
4. Controler enfin la trace correspondante dans l audit pour confirmer le retour a un etat coherent.

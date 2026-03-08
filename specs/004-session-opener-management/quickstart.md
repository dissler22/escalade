# Quickstart: Gestion des responsables de pratique libre

## Goal

Verifier rapidement le parcours manuel puis le parcours automatise de la feature `responsable` dans le monolithe Django existant.

## Preconditions

- Branche courante: `004-session-opener-management`
- Environnement virtuel du repo disponible
- Base locale initialisee
- Au moins trois comptes de test:
  - un `admin`
  - un `member`
  - un `member` accreditable comme `responsable`
- Une configuration email de test disponible si l on veut verifier les notifications sortantes

## Local validation flow

1. Lancer les migrations et le serveur local.
2. Creer ou mettre a jour une seance de plus de `1h30`.
3. Verifier que la seance est decoupee en plusieurs creneaux de `90 minutes max`.
4. Depuis un compte admin, accrediter un adherent comme responsable.
5. Depuis le compte responsable sur smartphone ou viewport mobile:
   - ouvrir la liste des seances
   - ouvrir le detail d une seance
   - prendre la responsabilite d un creneau sans responsable
   - verifier que le meme creneau refuse un second responsable
6. Verifier qu un responsable peut aussi rester inscrit comme pratiquant sur le meme creneau.
7. Depuis l admin:
   - retirer l accreditation responsable
   - verifier que les futures affectations du compte sont revoquees
   - verifier que le creneau redevient non couvert
8. Executer le traitement planifie en mode manuel sur des donnees de test:
   - scenario `J-7` pour un creneau non couvert
   - scenario `J-2` pour un creneau non couvert
   - commande: `.venv/bin/python src/manage.py process_slot_coverage_deadlines`
9. Verifier:
   - les emails emis
   - l annulation du seul creneau cible
   - la conservation des autres creneaux de la meme seance
   - les traces d audit associees

## Suggested verification commands

```bash
cd /home/marius/work/repos/escalade
.venv/bin/python src/manage.py migrate
.venv/bin/python src/manage.py runserver
pytest
```

## Test focus

- `tests/unit/`
  - decoupage des seances en creneaux
  - validation de l accreditation responsable
  - prevention du double responsable actif
  - traitement `J-7` et `J-2`
- `tests/integration/`
  - parcours membre/responsable
  - correction admin
  - annulation ciblee d un seul creneau
  - exposition de l adresse d envoi en administration
- `tests/contract/`
  - presence des nouveaux chemins de contrat pour responsabilite, accreditations et notifications

## Manual recovery drill

1. Desactiver volontairement l envoi email de test.
2. Executer le traitement planifie.
3. Verifier que l admin voit toujours les creneaux non couverts ou annules.
4. Couvrir ou annuler manuellement un creneau puis prevenir les inscrits depuis la boite dediee.
5. Verifier que l historique garde la trace de l operation manuelle et de l echec d automatisation si ce cas est trace.

## Daily manual recovery

1. Ouvrir `/admin/accounts/` pour verifier l adresse d envoi visible.
2. Ouvrir `/admin/sessions/` pour reperer les seances avec creneaux sans responsable.
3. Corriger un responsable ou annuler un seul creneau depuis la fiche admin de la seance.
4. Si besoin, executer manuellement `.venv/bin/python src/manage.py process_slot_coverage_deadlines`.

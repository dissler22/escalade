# Deployment Artifacts

Ce dossier contient les artefacts a copier ou adapter sur la VM cible `instance-20260307-190711`.

## Inventaire

- `nginx/escalade.conf`: frontal HTTP public pour `34.71.54.146`
- `systemd/escalade.service`: service Gunicorn gere par systemd

## Conventions de layout

- Code publie dans `/srv/escalade/releases/<release_id>/`
- Release active exposee par le lien `/srv/escalade/current`
- Etat partage dans `/srv/escalade/shared/`
- Configuration hors repo dans `/srv/escalade/shared/config/escalade.env`
- Base SQLite dans `/srv/escalade/shared/db/escalade.sqlite3`
- Fichiers statiques publies dans `/srv/escalade/shared/static/`
- Journaux dans `/srv/escalade/shared/log/`

## Proprietaire et droits

- Proprietaire applicatif: utilisateur systeme `escalade`
- Groupe frontal: `www-data`
- Dossiers `releases/`, `shared/`, `shared/db`, `shared/static`, `shared/log`: droits `0750`
- Fichier `shared/config/escalade.env`: droits `0640`
- Fichier SQLite et sauvegardes: droits `0640`

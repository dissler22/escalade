# Deployment

## Cible

- VM Google Cloud `instance-20260307-190711`
- Zone `us-central1-f`
- Projet Google Cloud `escalade-489519`
- IP publique initiale `34.71.54.146`
- Stack: Nginx + Gunicorn + Django + SQLite sur la meme machine

## Acces SSH operateur

- L'acces SSH operateur valide depuis un terminal local passe par `gcloud`, pas par un `ssh user@34.71.54.146` brut.
- Authentifier d'abord le poste local avec `gcloud auth login`.
- Selectionner ensuite le projet avec `gcloud config set project escalade-489519`.
- Ouvrir une session avec `gcloud compute ssh instance-20260307-190711 --zone=us-central1-f`.
- Au premier lancement, `gcloud` peut generer une paire de cles SSH locale dans `~/.ssh/`.
- Une fois l'acces `gcloud compute ssh` valide, generer les alias SSH locaux avec `gcloud compute config-ssh` si besoin.

## Exigences machine

- Ubuntu LTS recente
- Debian 12 ou Ubuntu LTS recente
- `python3` et `python3-venv`
- Nginx
- `sqlite3`
- `curl`
- `systemd`

## Ports exposes

- `22/tcp` pour l'administration SSH
- `80/tcp` pour l'acces public HTTP initial
- `443/tcp` seulement apres ajout ulterieur d'un certificat et d'un nom de domaine
- `8001/tcp` ne doit pas etre expose qu'en loopback locale

## Layout de release

- `/srv/escalade/releases/<release_id>`: code d'une release
- `/srv/escalade/current`: lien symbolique vers la release active
- `/srv/escalade/shared/config/escalade.env`: configuration runtime hors repo
- `/srv/escalade/shared/db/escalade.sqlite3`: base de production persistante
- `/srv/escalade/shared/static/`: resultat de `collectstatic`
- `/srv/escalade/shared/backups/`: sauvegardes SQLite horodatees
- `/srv/escalade/shared/log/`: logs applicatifs et journal d'exploitation
- `/srv/escalade/shared/venv/`: virtualenv reutilisee entre releases

## Checklist premiere mise en ligne

1. Executer `scripts/deploy/provision_vm.sh` en root ou via `sudo`.
2. Copier `docs/deploy/nginx/escalade.conf` vers `/etc/nginx/sites-available/escalade.conf` puis activer le site.
3. Copier `docs/deploy/systemd/escalade.service` vers `/etc/systemd/system/escalade.service`.
4. Creer `/srv/escalade/shared/config/escalade.env` a partir de `.env.example`.
5. Verifier que `PYTHON_BIN`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` et `APP_DATABASE_PATH` pointent vers les chemins de production.
6. Lancer `scripts/deploy/first_release.sh <source_dir>`.
7. Activer Nginx et le service `escalade`, puis verifier `http://34.71.54.146/login/`.
8. Executer `scripts/deploy/smoke_check.sh http://34.71.54.146`.

## Permissions et proprietes

- Proprietaire du layout applicatif: `escalade`
- Groupe frontal: `www-data`
- Dossiers `releases`, `shared`, `shared/db`, `shared/static`, `shared/backups`, `shared/log`: `0750`
- Fichier `.env` de production: `0640`
- Base SQLite et sauvegardes: `0640`
- Nginx lit `shared/static`; Gunicorn lit `shared/config` et ecrit dans `shared/log`

## Verification apres reboot

1. Redemarrer la VM.
2. Verifier `systemctl status escalade` puis `systemctl status nginx`.
3. Rejouer `scripts/deploy/smoke_check.sh http://34.71.54.146`.
4. Confirmer que `/sessions/`, `/bookings/mine/` et `/static/css/app.css` repondent correctement apres authentification.

## Rollback

1. Toujours creer une sauvegarde via `scripts/deploy/backup_sqlite.sh` avant une release.
2. En cas d'echec de migration, restaurer la sauvegarde puis reactiver la release precedente avec `scripts/deploy/rollback.sh`.
3. En cas d'echec du smoke test sans corruption de donnees, rebasculer seulement la release precedente.
4. Verifier apres rollback le parcours connexion -> seances -> mes reservations.

## Repli manuel

- Si la web app est indisponible, tenir temporairement une liste externe.
- Une fois le service revenu, ressaisir si besoin les corrections depuis l'interface admin.
- Noter toute correction manuelle dans le journal d'exploitation.

## Notes finales

- Aucun composant payant ou service managé n'est requis pour cette premiere mise en ligne.
- SQLite reste acceptable pour la charge cible tant que les ecritures simultanees restent faibles et que les sauvegardes sont disciplinees.

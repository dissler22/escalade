# Deployment

## Cible

- VM Google Cloud `instance-20260307-190711`
- Zone `us-central1-f`
- Projet Google Cloud `escalade-489519`
- IP publique initiale `34.71.54.146`
- Domaine de production `usmviroflayscalade.fr`
- Stack: Nginx + Gunicorn + Django + SQLite sur la meme machine

## Acces SSH operateur

- L'acces SSH operateur valide depuis un terminal local passe par `gcloud`, pas par un `ssh user@34.71.54.146` brut.
- Authentifier d'abord le poste local avec `gcloud auth login`.
- Selectionner ensuite le projet avec `gcloud config set project escalade-489519`.
- Ouvrir une session avec `gcloud compute ssh instance-20260307-190711 --zone=us-central1-f`.
- Au premier lancement, `gcloud` peut generer une paire de cles SSH locale dans `~/.ssh/`.
- Une fois l'acces `gcloud compute ssh` valide, generer les alias SSH locaux avec `gcloud compute config-ssh` si besoin.

## Mise a jour de production depuis des modifications locales

Cette procedure sert a publier l'etat courant du depot local sur la VM, sans supposer un push Git intermediaire.

### Principes

- Verifier et figer d'abord les modifications locales a deployer.
- Transferer une copie propre du depot vers un repertoire temporaire sur la VM.
- Lancer `scripts/deploy/release.sh` sur la VM, jamais un copier-coller manuel vers `/srv/escalade/current`.
- Laisser la base, les fichiers statiques, le virtualenv partage et le rollback sous le controle des scripts de release.

### Checklist locale avant transfert

1. Verifier les fichiers modifies avec `git status --short`.
2. Executer au minimum les verifications utiles depuis le poste local:
   - `cd src && pytest`
   - `cd src && python manage.py check`
   - `ruff check .`
3. Supprimer ou exclure les fichiers de debug qui n'ont rien a faire en production.
4. Noter un identifiant de release lisible, par exemple `20260419-session-access-types`.

### Transfert du code vers la VM

Depuis le poste local:

1. Construire une archive locale du working tree courant:
   - `tar --exclude=.git --exclude=.venv --exclude=.pytest_cache --exclude=.ruff_cache --exclude=__pycache__ -czf /tmp/escalade-release.tar.gz .`
2. Copier l'archive sur la VM:
   - `gcloud compute scp --zone=us-central1-f /tmp/escalade-release.tar.gz instance-20260307-190711:/tmp/escalade-release.tar.gz`
3. Preparer le repertoire de travail distant et decompresser l'archive:
   - `gcloud compute ssh instance-20260307-190711 --zone=us-central1-f --command='rm -rf /tmp/escalade-release && mkdir -p /tmp/escalade-release && tar -xzf /tmp/escalade-release.tar.gz -C /tmp/escalade-release'`

Notes:

- L'archive contient l'etat local courant, y compris les fichiers non suivis non exclus. Il faut donc nettoyer le depot avant emballage si certains fichiers ne doivent pas partir en production.
- `git archive` n'est pas adapte ici, car il ignore les modifications locales non committees.
- Le script `release.sh` exclut `.git`, `.venv` et `__pycache__` au moment de construire la release, mais il ne filtre pas les autres fichiers de travail.

### Execution de la release sur la VM

Une fois le code transfere, ouvrir une session SSH operateur puis lancer la release avec `sudo`:

1. `gcloud compute ssh instance-20260307-190711 --zone=us-central1-f`
2. `cd /tmp/escalade-release`
3. `sudo scripts/deploy/release.sh /tmp/escalade-release 20260419-session-access-types`

Ce que fait `scripts/deploy/release.sh`:

- charge la configuration runtime depuis `/srv/escalade/shared/config/escalade.env`
- cree une sauvegarde SQLite horodatee avant de toucher a la release
- copie le code dans `/srv/escalade/releases/<release_id>`
- installe les dependances Python dans `/srv/escalade/shared/venv`
- execute `migrate` puis `collectstatic`
- bascule le lien `/srv/escalade/current` vers la nouvelle release
- redemarre `escalade` et `nginx`
- lance `scripts/deploy/smoke_check.sh`

### Verification immediate apres release

Sur la VM:

1. Verifier le retour de `release.sh`. La commande doit finir sans erreur.
2. Verifier que les variables de smoke test sont bien configurees dans `/srv/escalade/shared/config/escalade.env` si `release.sh` a lance `scripts/deploy/smoke_check.sh`.
3. Verifier les services:
   - `sudo systemctl status escalade --no-pager`
   - `sudo systemctl status nginx --no-pager`
4. Consulter les logs si besoin:
   - `sudo journalctl -u escalade -n 100 --no-pager`
   - `sudo tail -n 100 /srv/escalade/shared/log/django.log`
   - `sudo tail -n 100 /srv/escalade/shared/log/operations.log`
5. Rejouer manuellement le smoke test si necessaire:
   - `sudo scripts/deploy/smoke_check.sh https://usmviroflayscalade.fr`

### Nettoyage apres deploiement

- Supprimer le repertoire temporaire de transfert une fois la release validee:
  - `rm -rf /tmp/escalade-release`
- Supprimer aussi l'archive temporaire:
  - `rm -f /tmp/escalade-release.tar.gz`
- Conserver l'identifiant de release et l'heure de deploiement dans le journal d'exploitation.

### Si la release echoue

1. Identifier la release precedente:
   - `ls -1dt /srv/escalade/releases/*`
2. Relancer vers la release precedente:
   - `sudo scripts/deploy/rollback.sh`
3. Si la base doit etre restauree, fournir explicitement le fichier de sauvegarde cree par `release.sh`:
   - `sudo scripts/deploy/rollback.sh <release_id_precedent> <backup_file>`
4. Verifier ensuite:
   - `sudo systemctl status escalade --no-pager`
   - `sudo scripts/deploy/smoke_check.sh https://usmviroflayscalade.fr`

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
- `443/tcp` pour l'acces public HTTPS avec certificat Let s Encrypt
- `8001/tcp` ne doit pas etre expose qu'en loopback locale

## Nom de domaine et HTTPS

Le site de production repond sur `https://usmviroflayscalade.fr`.

Ordre de mise en place recommande:

1. Verifier dans Google Cloud que l IP externe de la VM est bien reservee en statique.
2. Creer chez OVH un enregistrement DNS `A` pour `usmviroflayscalade.fr` vers `34.71.54.146`.
3. Attendre la propagation puis verifier depuis un poste operateur avec `dig +short usmviroflayscalade.fr`.
4. Mettre a jour la configuration Nginx de la VM pour utiliser `server_name usmviroflayscalade.fr;`.
5. Mettre a jour `/srv/escalade/shared/config/escalade.env` avec:
   - `DJANGO_ALLOWED_HOSTS=usmviroflayscalade.fr`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=http://usmviroflayscalade.fr,https://usmviroflayscalade.fr`
6. Verifier Nginx puis recharger les services:
   - `sudo nginx -t`
   - `sudo systemctl reload nginx`
   - `sudo systemctl restart escalade`
7. Installer Certbot si necessaire:
   - `sudo apt-get update`
   - `sudo apt-get install -y certbot python3-certbot-nginx`
8. Demander ou renouveler le certificat:
   - `sudo certbot --nginx --non-interactive --agree-tos --expand -m <email-operateur> -d usmviroflayscalade.fr --redirect`
9. Verifier ensuite:
   - `curl -I http://usmviroflayscalade.fr/login/` doit rediriger en `301` vers HTTPS
   - `curl -I https://usmviroflayscalade.fr/login/` doit repondre en `200`

Notes:

- Le certificat Let s Encrypt actuellement deploye couvre `usmviroflayscalade.fr`.
- Un certificat valide ne garantit pas a lui seul l indicateur navigateur vert. Une page peut encore etre marquee non securisee si elle charge une ressource en `http://`.
- Si un second nom doit etre ajoute plus tard, l inclure partout: DNS, `server_name`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` et commande `certbot`.

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
7. Verifier la resolution DNS de `usmviroflayscalade.fr` vers l IP publique de la VM.
8. Activer Nginx et le service `escalade`, puis verifier `https://usmviroflayscalade.fr/login/`.
9. Executer `scripts/deploy/smoke_check.sh https://usmviroflayscalade.fr`.

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
3. Rejouer `scripts/deploy/smoke_check.sh https://usmviroflayscalade.fr`.
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

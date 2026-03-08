# Deployment Scripts

Scripts shell pour une mise en production simple sur VM unique.

## Scripts

- `common.sh`: variables et fonctions communes de layout, log et validation
- `provision_vm.sh`: prepare une VM vierge
- `first_release.sh`: effectue la premiere installation applicative
- `smoke_check.sh`: verifie le point d'entree public et le parcours authentifie minimal
- `backup_sqlite.sh`: prend une sauvegarde SQLite horodatee
- `restore_sqlite.sh`: restaure une sauvegarde SQLite
- `release.sh`: publie une nouvelle release dans un repertoire horodate
- `rollback.sh`: rebascule vers une release precedente et restaure la base si besoin

## Usage

- Ces scripts sont destines a etre executes depuis un shell Bash sur la VM.
- Les scripts qui touchent aux paquets systeme ou a `systemd` doivent etre lances avec `sudo`.
- La configuration runtime est chargee depuis `APP_ENV_FILE` ou `/srv/escalade/shared/config/escalade.env`.

# Data Model - Deploiement VM simple

Ce modele decrit les objets operationnels necessaires au deploiement sur VM. Ils ne correspondent pas tous a des tables applicatives; certains peuvent vivre sous forme de fichiers, de liens symboliques ou d'unites systeme.

## 1. RuntimeConfig

### Purpose

Represente la configuration d'execution de l'environnement de production, conservee hors du depot.

### Fields

- `environment_name`: identifiant de l'environnement, par exemple `production`
- `secret_key`
- `debug_enabled`
- `allowed_hosts`
- `database_path`
- `static_root_path`
- `log_path`
- `updated_at`
- `updated_by`

### Validation Rules

- `secret_key` doit etre non vide et differente de toute valeur de test.
- `debug_enabled` doit etre `false` en production.
- `allowed_hosts` doit contenir au minimum l'IP publique ou le nom d'hote de production.
- `database_path`, `static_root_path` et `log_path` doivent pointer vers des repertoires persistants accessibles par les services.

### Relationships

- Un `RuntimeConfig` actif est utilise par une `DeploymentRelease`.
- Un `RuntimeConfig` reference le `SharedStateDirectory` pour ses chemins persistants.

## 2. SharedStateDirectory

### Purpose

Represente l'espace persistant de la VM qui survit aux releases successives.

### Fields

- `root_path`
- `database_file`
- `backups_path`
- `static_path`
- `env_file_path`
- `operations_log_path`
- `retention_policy`

### Validation Rules

- Tous les sous-repertoires critiques doivent exister avant la premiere release.
- Les fichiers de donnees et de configuration ne doivent pas etre stockes dans un dossier de release jetable.
- L'espace disque disponible doit rester compatible avec au moins une release active et plusieurs sauvegardes recentes.

### Relationships

- Un `SharedStateDirectory` supporte plusieurs `DeploymentRelease`.
- Un `SharedStateDirectory` contient plusieurs `BackupSnapshot`.

## 3. DeploymentRelease

### Purpose

Represente une version publiable du code deployee sur la VM.

### Fields

- `release_id`: identifiant horodate ou hash court
- `revision_ref`
- `release_path`
- `activated_at`
- `activated_by`
- `migration_status`: `pending`, `applied`, `failed`
- `static_publish_status`: `pending`, `published`, `failed`
- `service_status`: `pending`, `running`, `failed`
- `verification_status`: `pending`, `passed`, `failed`
- `notes`

### Validation Rules

- Une release ne devient active qu'apres publication du code, des statics et redemarrage reussi.
- Une release avec `migration_status = failed` ne peut pas etre marquee `verification_status = passed`.
- Une seule `DeploymentRelease` peut etre active a la fois via le lien `current`.

### Relationships

- Une `DeploymentRelease` utilise un `RuntimeConfig`.
- Une `DeploymentRelease` peut s'appuyer sur un `BackupSnapshot` pre-release.
- Une `DeploymentRelease` produit plusieurs `PublicServiceCheck`.

### State Transitions

- `pending -> running` apres publication et redemarrage
- `running -> failed` si migration, demarrage ou verification echoue
- `failed -> rolled_back` apres reactivation d'une release precedente
- `running -> superseded` lorsqu'une release plus recente prend la place

## 4. BackupSnapshot

### Purpose

Represente une sauvegarde horodatee utilisable pour un rollback ou une reprise apres incident.

### Fields

- `snapshot_id`
- `created_at`
- `created_by`
- `database_copy_path`
- `related_release_id`
- `verification_checksum`: optionnel
- `restore_tested`
- `notes`

### Validation Rules

- Une sauvegarde pre-release doit exister avant toute operation modifiant schema ou donnees.
- Le fichier de sauvegarde doit etre lisible depuis la machine avant de continuer la release.
- Une sauvegarde associee a une release doit pouvoir etre rattachee sans ambiguite a la revision deployee.

### Relationships

- Un `BackupSnapshot` est cree avant une `DeploymentRelease`.
- Un `BackupSnapshot` peut etre utilise lors d'un rollback d'une `DeploymentRelease`.

## 5. PublicServiceCheck

### Purpose

Represente un controle de disponibilite visible depuis le reseau public ou depuis la machine.

### Fields

- `check_id`
- `release_id`
- `target_url`
- `expected_result`
- `actual_result`
- `checked_at`
- `checked_by`
- `status`: `passed`, `failed`

### Validation Rules

- Le lot minimal de verification couvre la page de connexion, la liste des seances et le CSS principal.
- Un echec sur un controle critique bloque la cloture reussie de la release.

### Relationships

- Plusieurs `PublicServiceCheck` appartiennent a une `DeploymentRelease`.

## Operational Rules

- Le lien symbolique ou pointeur equivalent `current` designe toujours une seule `DeploymentRelease` active.
- Les migrations et la publication des statics s'executent sur la release candidate avant exposition durable au trafic.
- Le fichier SQLite de production n'est jamais remplace sans sauvegarde horodatee prealable.
- Le rollback restaure d'abord le code precedent, puis les donnees si la release echec a laisse un etat incoherent.

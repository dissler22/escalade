# Quickstart - Deploiement VM simple

## Purpose

Verifier rapidement qu'une implementation couvre le MVP de deploiement sur une VM unique pour la feature `002-gcp-vm-deploy`.

## Preconditions

- La VM `instance-20260307-190711` est joignable en administration.
- Le depot ou un artefact de release est disponible pour etre copie sur la machine.
- Un fichier de configuration de production hors depot a ete prepare.
- Un repertoire persistant partage existe pour la base, les sauvegardes, les fichiers statiques et les traces de release.
- La base applicative de reference et au moins un compte administrateur existent deja ou peuvent etre initialises.

## Scenario 1: Provisionner la VM pour le premier deploiement

1. Installer Python cible, Nginx et le service applicatif WSGI sur la machine.
2. Creer un utilisateur systeme dedie a l'application.
3. Creer les repertoires persistants partages pour la configuration, la base, les sauvegardes et les statics.
4. Copier la configuration de production hors du depot dans le repertoire partage.
5. Verifier que les permissions machine permettent au service applicatif de lire la configuration et d'ecrire dans la base.

## Scenario 2: Publier la premiere release

1. Copier le code de la release dans un repertoire horodate.
2. Installer les dependances runtime dans l'environnement dedie.
3. Initialiser ou migrer la base de production dans son emplacement persistant.
4. Publier les fichiers statiques dans le repertoire partage.
5. Activer la release courante et demarrer les services.
6. Verifier que la page `/login/` repond puis que le CSS principal est charge.

## Scenario 3: Verifier le parcours public critique

1. Depuis un navigateur externe ou un smartphone, ouvrir `http://34.71.54.146/`.
2. Verifier la redirection vers la page de connexion.
3. Se connecter avec un compte valide.
4. Ouvrir la liste des seances.
5. Ouvrir `Mes reservations`.
6. Verifier qu'aucune page critique ne renvoie d'erreur serveur et que les styles sont appliques.

**Resultat attendu**:

- `/` redirige vers `/login/`
- `/login/` retourne `200`
- apres connexion, `/sessions/` retourne `200`
- `/bookings/mine/` retourne `200`
- `/static/css/app.css` retourne `200`

## Scenario 4: Rejouer une release standard avec sauvegarde

1. Creer une sauvegarde horodatee de la base de production.
2. Deployer une nouvelle release dans un nouveau repertoire.
3. Appliquer les migrations et republier les statics.
4. Redemarrer les services.
5. Rejouer le smoke test de connexion puis liste des seances.
6. Consigner dans le journal d'exploitation la revision active et l'emplacement de la sauvegarde.

**Journal minimum**:

- operateur
- release candidate
- release active precedente
- sauvegarde SQLite associee
- resultat du smoke test

## Scenario 5: Exercer le rollback

1. Simuler un echec applicatif sur la release candidate ou choisir une release volontairement invalide.
2. Rebasculer le pointeur de release vers la version precedente.
3. Restaurer la sauvegarde pre-release si les donnees ou migrations ont ete rendues incoherentes.
4. Redemarrer les services.
5. Verifier a nouveau `/login/`, `/sessions/` et `/bookings/mine/`.
6. Noter l'incident et la resolution dans le journal d'exploitation.

**Resultat attendu**:

- la release precedente redevient active en moins de 20 minutes
- les pages `/login/`, `/sessions/` et `/bookings/mine/` repondent a nouveau
- la base SQLite restauree reste coherente avec la release active

## Scenario 6: Verifier la resilience apres reboot

1. Redemarrer la VM ou les services.
2. Verifier que le frontal web et le service applicatif reviennent sans intervention supplementaire.
3. Rejouer le smoke test public minimal.

## Validation Notes

- Le deploiement MVP est valide si le parcours connexion puis liste des seances fonctionne depuis l'IP publique.
- Les fichiers statiques doivent rester servis correctement apres redemarrage de service et apres reboot machine.
- La release standard doit toujours commencer par une sauvegarde exploitable.
- Le rollback est valide seulement si la version precedente redevient accessible avec des donnees coherentes.

## Smoke Checklist Outcomes

- Validation locale pytest: OK le 2026-03-07 (`23` tests)
- Provisionnement VM: a executer sur `instance-20260307-190711`
- Publication premiere release: a executer sur `34.71.54.146`
- Connexion publique et navigation mobile: a executer avec `scripts/deploy/smoke_check.sh`
- Reboot resilience: a executer apres reboot de la VM
- Rollback manuel documente: a executer avec une release de test

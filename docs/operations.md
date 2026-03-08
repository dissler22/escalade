# Operations

## Comptes

- les comptes sont pre-crees par un administrateur ou via l'admin Django
- un compte inactif ne peut plus se connecter ni reserver
- en cas de mot de passe perdu, l'admin regenere un mot de passe temporaire depuis l'admin Django
- les donnees exploitees au quotidien sont limitees au nom affiche, a l'email, au role, au statut d'activation, aux seances, aux reservations et aux traces d'audit
- les ecrans membre n'exposent que les seances reservables et les reservations du compte courant

## Journal d'exploitation

- consigner chaque premiere mise en ligne, release, rollback et restauration dans `/srv/escalade/shared/log/operations.log`
- inclure la date, l'operateur, la release active, l'emplacement de sauvegarde et le resultat du smoke test
- conserver les journaux systeme `journalctl -u escalade` et `journalctl -u nginx` pour la meme fenetre d'incident
- ne jamais y recopier de mot de passe, de cookie de session ou de secret complet

## Seances

- creer les series ou occurrences en avance
- verifier le statut `open` avant ouverture au club
- en cas d'erreur de capacite ou de statut, corriger la seance depuis l'ecran admin des seances

## Reservations

- si un adherent affirme avoir reserve sans preuve visible, ouvrir la fiche admin des inscrits puis l'historique
- si la reservation manque, l'admin peut l'ajouter manuellement si la seance est encore future et capacitaire
- si une reservation doit etre retiree, l'admin la supprime depuis la fiche des inscrits pour garder une trace d'audit
- en cas de reservation contestee sur une seance fermee, l'admin peut encore corriger manuellement une seance future sans rouvrir publiquement les inscriptions

## Reprise manuelle

- si la web app est indisponible, tenir une liste temporaire externe
- des que le service revient, re-saisir les reservations manquantes depuis les ecrans admin
- verifier ensuite l'historique de la seance pour confirmer la correction

## Fenetre de maintenance

- annoncer une fenetre courte avant toute release qui modifie la base ou les statics
- prendre une sauvegarde SQLite juste avant de lancer la release
- interdire toute edition manuelle de la base pendant le deploiement ou le rollback

## Procedure de rollback

1. Identifier la derniere release saine et la sauvegarde associee.
2. Lancer `scripts/deploy/rollback.sh <release_id_precedent> [backup_file]`.
3. Verifier `systemctl status escalade`.
4. Rejouer le smoke test public.
5. Noter la cause, l'heure de debut, l'heure de fin et les actions correctives dans le journal d'exploitation.

## Retention et minimisation

- ne conserver dans `.env` que les secrets et chemins strictement necessaires au runtime
- garder les sauvegardes SQLite recentes utiles a la reprise, puis supprimer les plus anciennes selon la place disque disponible
- conserver le journal d'exploitation et les journaux systeme pour les incidents actifs et les retours d'experience utiles

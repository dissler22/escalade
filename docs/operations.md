# Operations

## Comptes

- les comptes sont pre-crees par un administrateur ou via l'admin Django
- un compte inactif ne peut plus se connecter ni reserver
- en cas de mot de passe perdu, l'admin regenere un mot de passe temporaire depuis l'admin Django
- les donnees exploitees au quotidien sont limitees au nom affiche, a l'email, au role, au statut d'activation, aux seances, aux reservations et aux traces d'audit
- les ecrans membre n'exposent que les seances reservables et les reservations du compte courant

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

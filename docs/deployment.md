# Deployment

## Hypotheses

- hebergement associatif ou gratuit
- stockage relationnel leger
- sauvegarde reguliere de la base via export planifie

## Options sobres

- Railway ou Render en offre minimale si un hebergement externe est necessaire
- SQLite pour demo ou usage local
- PostgreSQL partage si plusieurs admins modifient en meme temps

## Repli

- en cas d'indisponibilite, l'administration peut revenir temporairement a une liste manuelle
- la reprise se fait par recreation ou correction manuelle des seances et reservations depuis les ecrans admin

## Rollback

- avant chaque mise en production, conserver une sauvegarde de la base
- si une version degrade le parcours critique, redeployer la version precedente puis rejouer uniquement les corrections manuelles necessaires
- verifier apres rollback les seances ouvertes et l'historique d'audit des corrections appliquees

## Notes finales

- aucune dependance payante n'est requise pour le fonctionnement nominal de la V1
- un hebergement gratuit ou tres faible cout reste suffisant tant que le club garde un volume limite de comptes et de seances

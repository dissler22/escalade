# Quickstart - Reservations de seances libres

## Purpose

Verifier rapidement qu'une implementation couvre le MVP fonctionnel attendu pour la feature `001-free-session-booking`.

## Preconditions

- Une application locale ou de demonstration expose la web app mobile-first.
- Au moins un compte `admin` et deux comptes `member` existent.
- L'historique d'audit est consultable par un administrateur.

## Scenario 1: Creer et ouvrir une seance ponctuelle

1. Se connecter avec un compte administrateur.
2. Creer une seance ponctuelle future avec une capacite de `16`.
3. Verifier que la seance apparait dans la liste admin avec le statut souhaite.
4. Ouvrir la seance si elle ne l'est pas deja.
5. Verifier qu'une trace d'audit existe pour la creation puis pour l'ouverture.

## Scenario 2: Reserver une place depuis un telephone

1. Ouvrir la web app depuis un viewport smartphone.
2. Se connecter avec un compte `member`.
3. Consulter les seances ouvertes a venir.
4. Ouvrir le detail de la seance creee au scenario 1.
5. Reserver une place.
6. Verifier que la reservation apparait dans l'espace personnel.
7. Verifier que le nombre de places restantes a diminue.

## Scenario 3: Empencher les sur-reservations

1. Configurer une seance ouverte avec une capacite faible, par exemple `1`.
2. Reserver la place avec un premier compte `member`.
3. Tenter de reserver la meme seance avec un second compte `member`.
4. Verifier que la seconde tentative est refusee avec un message clair.
5. Verifier que la capacite n'est jamais negative.

## Scenario 4: Annuler puis liberer une place

1. Avec le premier compte `member`, annuler une reservation sur une future seance.
2. Verifier que la reservation n'apparait plus comme active pour ce membre.
3. Verifier que la place redevient disponible.
4. Verifier qu'une trace d'audit d'annulation existe.

## Scenario 5: Corriger manuellement cote admin

1. Se reconnecter avec le compte `admin`.
2. Ouvrir la liste des inscrits d'une seance future.
3. Ajouter manuellement une reservation pour un membre autorise.
4. Retirer ensuite cette reservation.
5. Verifier que les deux actions sont visibles dans l'historique d'audit.

## Scenario 6: Modifier une serie sans casser une semaine isolee

1. Creer une serie hebdomadaire avec capacite `30`.
2. Generer ou verifier l'existence d'au moins deux occurrences futures.
3. Modifier une seule occurrence pour fixer sa capacite a `16`.
4. Verifier que l'autre occurrence conserve `30`.
5. Modifier ensuite la serie et verifier que l'occurrence deja surchargee garde sa valeur specifique tant qu'elle n'est pas explicitement re-alignee.

## Validation Notes

- Smartphone MVP valide localement: connexion, consultation des seances ouvertes, reservation, affichage dans `Mes reservations`, annulation.
- Controle capacitaire valide: une seule place restante ne peut pas etre sur-reservee.
- Corrections admin valides: ajout manuel, retrait manuel, fermeture d'une seance et consultation de l'historique.
- La validation repose actuellement sur les tests Django automatises et une base locale SQLite.

## Smoke Checklist Outcomes

- Parcours membre critique: OK
- Creation d'une occurrence ponctuelle: OK
- Creation d'une serie et generation d'occurrences: OK
- Override d'une seule semaine: OK
- Consultation de l'historique d'audit: OK

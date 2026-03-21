# escalade

Application web de reservation pour une section escalade, construite avec Django.

## Stack

- Python
- Django 5
- Templates Django server-side
- SQLite
- Gunicorn
- Nginx

## Fonctionnalites

- authentification des adherents
- consultation des seances
- reservation et annulation
- espace "mes reservations"
- ecrans d'administration pour les sessions et les comptes

## Demarrage local

Prerequis :

- Python 3.12+
- un environnement virtuel actif

Installation et lancement :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python src/manage.py migrate
python src/manage.py createsuperuser
python src/manage.py runserver
```

L'application est ensuite accessible sur `http://127.0.0.1:8000/login/`.

## Tests

```bash
source .venv/bin/activate
pytest
```

## Deploiement

Le deploiement cible une VM Linux avec :

- Gunicorn comme serveur WSGI
- Nginx en frontal
- SQLite sur stockage persistant local

Les scripts et la documentation de deploiement sont dans :

- `scripts/deploy/`
- `docs/deployment.md`

## Structure

- `src/` : projet Django et applications metier
- `tests/` : tests unitaires et d'integration
- `docs/` : documentation d'exploitation et de deploiement

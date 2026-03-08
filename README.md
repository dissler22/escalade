# escalade

Web app mobile-first de reservation de seances libres pour une section escalade.

## Demarrage local

```bash
source .venv/bin/activate
python src/manage.py migrate
python src/manage.py createsuperuser
python src/manage.py runserver
```

## Runtime de production

- Python systeme de la VM cible, configure via `PYTHON_BIN` (`python3` par defaut)
- Gunicorn comme serveur WSGI
- Nginx en frontal HTTP
- SQLite persistante sur la meme machine

## Commandes operateur

```bash
source .venv/bin/activate
python -m pytest
python src/manage.py collectstatic --noinput
python src/manage.py migrate
gunicorn --chdir src --bind 127.0.0.1:8001 config.wsgi:application
```

Les scripts et runbooks de deploiement sont dans `scripts/deploy/` et `docs/deployment.md`.

## Structure

- `src/` contient le projet Django et les applications metier.
- `tests/` contient les tests unitaires, d'integration et de contrat.
- `specs/001-free-session-booking/` contient la spec, le plan et les taches.
- `specs/002-gcp-vm-deploy/` contient la spec, le plan et les taches du deploiement VM.

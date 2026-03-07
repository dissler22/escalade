# escalade

Web app mobile-first de reservation de seances libres pour une section escalade.

## Demarrage local

```bash
source .venv/bin/activate
python src/manage.py migrate
python src/manage.py createsuperuser
python src/manage.py runserver
```

## Structure

- `src/` contient le projet Django et les applications metier.
- `tests/` contient les tests unitaires, d'integration et de contrat.
- `specs/001-free-session-booking/` contient la spec, le plan et les taches.

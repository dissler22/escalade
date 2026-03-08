# escalade Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-07

## Active Technologies
- Python 3.12+ dans le repo actuel, cible normalisee sur Python 3.13 pour la VM + Django 5.x, Gunicorn, Nginx, systemd, SQLite standard library support (002-gcp-vm-deploy)
- SQLite sur repertoire persistant partage de la VM + sauvegardes horodatees sur la meme machine (002-gcp-vm-deploy)
- Python 3.12+ dans le repo actuel + Django 5.x, templates Django server-side, feuille de style statique unique, authentification/session Django (003-club-visual-refresh)
- SQLite applicatif existant, sans changement de schema requis pour cette feature (003-club-visual-refresh)

- Python 3.13 + Django 5.x, Django authentication/session framework, PostgreSQL driver (001-free-session-booking)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.13: Follow standard conventions

## Recent Changes
- 003-club-visual-refresh: Added Python 3.12+ dans le repo actuel + Django 5.x, templates Django server-side, feuille de style statique unique, authentification/session Django
- 002-gcp-vm-deploy: Added Python 3.12+ dans le repo actuel, cible normalisee sur Python 3.13 pour la VM + Django 5.x, Gunicorn, Nginx, systemd, SQLite standard library support

- 001-free-session-booking: Added Python 3.13 + Django 5.x, Django authentication/session framework, PostgreSQL driver

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

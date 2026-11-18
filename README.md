# ROOM ARENA — Phase 1

Responsive Django + installable PWA tournament-management starter for an independent Free Fire MAX community Clash Squad (4v4) platform.

## Render deployment

1. Push this repository to GitHub (already connected to this repository).
2. In Render, create a **PostgreSQL** database. Copy its **Internal Database URL**.
3. Create a **Web Service** from `pk8873/free-fire-game-` (branch: `main`).
4. Set:
   - Build command: `bash build.sh`
   - Start command: `gunicorn config.wsgi:application`
   - Runtime: Python 3.12
5. Add environment variables:
   - `SECRET_KEY`: a long random secret (Render can generate one)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`
   - `CSRF_TRUSTED_ORIGINS`: `https://*.onrender.com`
   - `DATABASE_URL`: the PostgreSQL **Internal Database URL**
6. Deploy. In the service Shell run `python manage.py createsuperuser`, then sign in at `/admin/`.

You can also use Render Blueprint with `render.yaml`; it prompts for `DATABASE_URL` because database provisioning and plan availability vary by account/region.

## Local setup (Windows)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations players tournaments
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/admin/`.

## Current scope

- Responsive landing page, PWA manifest and service worker
- Tournament, player profile, team, team member, registration, match, room credential and match result data models
- Django Admin CRUD for Super Admin
- SQLite locally; PostgreSQL through `DATABASE_URL` in production
- Render build and start configuration

## Not yet implemented

Player-facing signup/login and dashboards, public team creation/join, player-side tournament registration, private room credential delivery, evidence uploads, dispute workflow, notifications, automated brackets and payments are not implemented yet. Four active team members are a tournament rule but are not yet enforced by a dedicated registration workflow. Super Admin must manually verify rosters and registrations.

## Legal and platform safety

This is an independent community project and is not affiliated with or endorsed by Garena. Do not use Garena trademarks, game artwork, sounds, or official branding without written permission. This version does not implement player deposits, paid-entry, betting, or wagering. Before commercial operation, prize promotions, or charging any fee, obtain qualified Indian legal advice and written permission/clarification from the relevant rights holder and authorities.

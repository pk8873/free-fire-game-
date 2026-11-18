# ROOM ARENA — Phase 1

Responsive Django + installable PWA tournament-management starter for Free Fire MAX community Clash Squad (4v4).

## Deploy on Render
1. Create a PostgreSQL database on Render.
2. Create a **Web Service** from this GitHub repository.
3. Runtime: Python 3.12. Build command: `./build.sh`. Start command: `gunicorn config.wsgi:application`.
4. Add environment variables: `SECRET_KEY` (long random value), `DEBUG=False`, `ALLOWED_HOSTS=.onrender.com`, `DATABASE_URL` (Render PostgreSQL Internal Database URL), `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`.
5. Deploy. Open `/admin/` and create a superuser from the Render Shell with `python manage.py createsuperuser`.

This is a community-run independent project, not affiliated with Garena. Phase 1 supports free-entry Clash Squad 4v4 only. No deposits, paid-entry, betting, or cash wagering are implemented. Obtain legal advice and written permissions before commercial use or use of game intellectual property. See `README_HI.md` for Hindi setup notes.

## Local setup
`py -3.12 -m venv .venv` then activate it, `python -m pip install -r requirements.txt`, `python manage.py migrate`, `python manage.py createsuperuser`, `python manage.py runserver`.

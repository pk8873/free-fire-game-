# ROOM ARENA — Phase 1 tournament platform

Independent Django + installable PWA community tournament platform. Current format: **Clash Squad 4v4**.

## Implemented player features

- Player signup with username, email, in-game name, unique Game UID and password
- Login/logout, player dashboard and profile editing
- Create a squad, join by invite code, view active roster
- Captain can transfer captaincy, remove squad members and rotate invite codes
- Members can leave a squad; captaincy must be transferred first
- Roster changes are blocked while a team has a pending or approved tournament registration
- Database constraint prevents a player from being active in multiple squads
- Public tournament detail pages; captain-only registration request
- Four active players required for Clash Squad registration
- Registration capacity checked inside a database transaction
- Player registration status

## Tournament/admin features

- Django Super Admin manages players, squads, tournaments, registrations, matches, room credentials, results and disputes
- Match room ID/password are hidden until the configured release time and only shown to approved participants in the assigned teams
- Captain can submit a provisional score; admin confirms it
- Participants from approved teams can report a match issue
- Disputed results are locked from further captain edits
- Admin can review/resolve disputes and edit final match records
- /health/ checks application database connectivity

## Platform

- Responsive dark/orange interface and PWA manifest/service worker
- SQLite locally; PostgreSQL via DATABASE_URL on Render
- Committed migrations, WhiteNoise static serving and GitHub Actions checks

## Render deployment — no Shell required for first admin

The app can create its first Super Admin during web startup using environment variables. **Never put the admin password in GitHub or in source code.**

1. In Render, open the existing ROOM ARENA Web Service → Environment.
2. Add these three environment variables (use your own values):
   - DJANGO_SUPERUSER_USERNAME — choose an admin username
   - DJANGO_SUPERUSER_EMAIL — your admin email
   - DJANGO_SUPERUSER_PASSWORD — choose a unique password with at least 12 characters
3. Save changes and trigger a deploy/redeploy. No Render Shell or createsuperuser command is needed.
4. When Gunicorn starts, the WSGI startup hook creates the superuser if that username does not already exist. It does not reset an existing user's password.
5. Open https://YOUR-SERVICE.onrender.com/admin/ and log in.

If the username already exists, the bootstrap deliberately does not change its password. If the app log says bootstrap skipped, verify all three environment variables and the 12-character minimum. Remove the bootstrap password variable after the first successful admin creation if you prefer; the existing admin account remains.

### Render service settings

- Runtime: Python 3.12
- Build command: bash build.sh
- Start command: gunicorn config.wsgi:application
- SECRET_KEY: generate a long secret in Render
- DEBUG: False
- ALLOWED_HOSTS: .onrender.com
- CSRF_TRUSTED_ORIGINS: https://*.onrender.com
- DATABASE_URL: PostgreSQL Internal Database URL

The Blueprint (render.yaml) includes the three admin bootstrap variables as secret prompts and configures /health/ as the health-check path. It does not create a PostgreSQL database automatically; provide an existing database URL. For an existing manually-created Render service, add the three bootstrap variables in its Environment page; changing GitHub code alone cannot create or set hosting secrets.

## Local setup (Windows / Python 3.12)

    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Home: http://127.0.0.1:8000/  
Admin: http://127.0.0.1:8000/admin/

## Still not implemented / limitations

- Automated single/double-elimination bracket generation and automatic match assignment
- Live game telemetry, automatic score verification, anti-cheat detection or Garena API integration
- Evidence/screenshot uploads and automated referee workflow
- Email/SMS/push notifications (SMTP/push provider not configured)
- Player password reset by email (requires verified email delivery configuration)
- Payment, wallet, entry fee, betting or wagering features are intentionally excluded
- High-concurrency stress testing, security audit and production backup/restore testing remain necessary

Admin manually approves registrations, creates matches, releases room details and confirms results. Submitted scores are provisional until admin confirmation.

## Rights and legal

ROOM ARENA is independent and is not affiliated with or endorsed by Garena. Do not use Garena logos, trademarks, game art, audio or official assets without permission. This repository does not grant tournament or commercial rights. Before public/commercial operation, prizes, sponsorship monetization or charging any fee, obtain written permission/clarification and qualified Indian legal advice.

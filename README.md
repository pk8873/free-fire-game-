# ROOM ARENA — Phase 1 Player Portal

ROOM ARENA is an independent Django + installable PWA community tournament platform. Current competition mode is **Clash Squad 4v4**.

## Features included

### Player side
- Player signup with username, email, in-game name and unique Game UID
- Login/logout and player dashboard
- Create a squad and share its invite code
- Join a squad using an invite code (maximum four active members)
- View published tournaments and request registration as team captain
- Registration status view (pending / approved / rejected)

### Tournament operations
- Super Admin manages tournaments, team registrations, match schedule and match status
- Admin adds room ID/password and a release timestamp
- Room details are only shown to logged-in players belonging to one of the two match teams, after the release timestamp, in an approved tournament
- A team captain can submit/update a provisional match result
- A participant from an approved team can file a match dispute
- Admin reviews/confirms results and resolves disputes

### Platform
- Responsive dark/orange interface
- PWA manifest and service worker
- SQLite for local development; PostgreSQL via DATABASE_URL in production
- Committed database migrations
- WhiteNoise static files and Render Blueprint configuration

## Deploy on Render

1. Open Render Dashboard and create a PostgreSQL database. Copy its **Internal Database URL**.
2. Create a Web Service from GitHub repository pk8873/free-fire-game-, branch main.
3. Runtime: Python 3.12.
4. Build command: bash build.sh
5. Start command: gunicorn config.wsgi:application
6. Add environment variables:
   - SECRET_KEY: long random secret (or let Render generate it)
   - DEBUG: False
   - ALLOWED_HOSTS: .onrender.com
   - CSRF_TRUSTED_ORIGINS: https://*.onrender.com
   - DATABASE_URL: PostgreSQL Internal Database URL
7. Deploy. In the Render service Shell run python manage.py createsuperuser.
8. Open your service URL plus /admin/ and sign in.

The render.yaml Blueprint asks for DATABASE_URL rather than creating a database automatically. Render database plans, free availability and retention can vary; check current terms in your account.

## Local setup (Windows / Python 3.12)

    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Open http://127.0.0.1:8000/. Admin: http://127.0.0.1:8000/admin/.

## Important limitations

This is a functional Phase 1 foundation, not a fully audited high-scale esports platform.

- No automated bracket generation, live scoring, push/email/SMS notifications, player evidence upload, anti-cheat verification or Garena API integration.
- Match scores are user-submitted and remain provisional until an admin confirms them. A dispute form is available; it is not an independent referee or evidence-verification system.
- Admin must create matches, approve registrations, release room details, and confirm results manually.
- Team size is checked when a captain requests tournament registration. The starter does not yet provide team-member removal, captain transfer or self-service team disband.
- Registration capacity checks are application-level; a high-concurrency production system needs database-level locking and additional load/security testing.
- No payment, entry-fee, wallet, betting or wagering feature is included.
- Render deployment and production database migrations have not been executed from this repository session. Run deployment and inspect logs before announcing the service as live.

## Legal / rights

ROOM ARENA is independent and is not affiliated with or endorsed by Garena. Do not use Garena logos, trademarks, game art, audio, or official assets without permission. This code does not grant tournament or commercial rights. Before public/commercial operation, prizes, sponsorship monetization or charging any fee, get written permission/clarification and qualified Indian legal advice.

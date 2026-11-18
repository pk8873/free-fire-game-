# ROOM ARENA — Hindi Setup Guide

यह Phase 1 Django + PWA starter है। इसमें Free Fire MAX community के लिए केवल Clash Squad 4v4 tournament listing और Super Admin के लिए Django Admin management शामिल है। यह अभी complete player self-service tournament portal नहीं है।

## Windows पर चलाएँ

1. Python 3.12 install करें और repository clone करें।
2. PowerShell में project folder खोलें:
   `py -3.12 -m venv .venv`
3. Activate करें: `\.venv\Scripts\Activate.ps1`
4. Packages install करें: `python -m pip install -r requirements.txt`
5. Database migration बनाएँ: `python manage.py makemigrations players tournaments`
6. Database tables बनाएँ: `python manage.py migrate`
7. Admin account बनाएँ: `python manage.py createsuperuser`
8. Server चलाएँ: `python manage.py runserver`
9. Home: `http://127.0.0.1:8000/` और Admin: `http://127.0.0.1:8000/admin/`

## Render पर Deploy

1. Render Dashboard में PostgreSQL database बनाएँ और उसका **Internal Database URL** copy करें।
2. GitHub repository `pk8873/free-fire-game-` से Web Service बनाएँ; branch `main) चुनें।
3. Build command: `bash build.sh`
4. Start command: `gunicorn config.wsgi:application`
5. Python runtime 3.12 चुनें।
6. Environment Variables जोड़ें:
   - `SECRET_KEY` = लंबी random secret value (Render generate कर सकता है)
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` = `https://*.onrender.com`
   - `DATABASE_URL` = PostgreSQL का Internal Database URL
7. Deploy के बाद Render Shell में `python manage.py createsuperuser` चलाएँ।
8. `https://YOUR-SERVICE.onrender.com/admin/` पर Super Admin login करें।

अगर Render Blueprint उपयोग करें तो `render.yaml` में `DATABASE_URL` manually भरना होगा। Database plan और availability region/account के अनुसार बदल सकते हैं।

## अभी शामिल सुविधाएँ

- Responsive landing page और PWA manifest/service worker
- Tournament, player profile, team, team member, registration, match, room credentials और result models
- Django Admin में Super Admin management
- Local SQLite और production PostgreSQL configuration
- Render build/start configuration

## अभी शामिल नहीं हैं

Player signup/login UI, player dashboard, public team create/join, player-side tournament registration, secure room credential delivery, proof uploads, dispute handling, notifications, auto brackets और payments अभी नहीं बने हैं। Exactly 4 active team members की rule अभी automated workflow से enforce नहीं होती; Admin को roster manually verify करना होगा।

## Legal / Permission

यह independent community platform है, Garena से affiliated या endorsed नहीं है। Garena logo, trademark, game artwork, sound या official branding written permission के बिना उपयोग न करें। इस version में player deposits, paid-entry, betting या wagering नहीं हैं। Commercial operation, prize promotion या कोई fee लेने से पहले qualified Indian lawyer और relevant rights holder/authority से written clarification लें।

# ROOM ARENA — Hindi Setup Guide

यह Phase 1 Django + PWA starter है। इसमें Free Fire MAX community के लिए केवल Clash Squad 4v4 का tournament listing और Super Admin के लिए Django Admin management दिया गया है। यह अभी complete player self-service portal नहीं है।

## Windows पर चलाएँ
1. Python 3.12 install करें और repository clone करें।
2. PowerShell में project folder खोलें: `py -3.12 -m venv .venv`
3. Activate: `\.venv\Scripts\Activate.ps1`
4. `python -m pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py createsuperuser`
7. `python manage.py runserver`
8. `http://127.0.0.1:8000/` और `http://127.0.0.1:8000/admin/` खोलें।

## Render Deploy
GitHub repo को Render में Web Service के रूप में जोड़ें। `render.yaml` Blueprint deploy भी उपयोग कर सकते हैं। यदि Blueprint free PostgreSQL plan उपलब्ध न हो, तो Render Dashboard में PostgreSQL अलग बनाएँ और उसका Internal Database URL `DATABASE_URL` में रखें। Build command `./build.sh`, start command `gunicorn config.wsgi:application` रखें। `SECRET_KEY` generate करें।

## अभी क्या शामिल है
- Responsive landing page और PWA manifest/service worker
- Tournament, team, registration, match, room credential और result के Django models
- Django Admin में Super Admin CRUD
- SQLite local और PostgreSQL production configuration
- Render build/deploy configuration

## अभी क्या नहीं है
Player signup/login screens, public team creation/join, player-side registration, private room credential delivery, evidence uploads, dispute workflow, notifications, payments और live bracket automation अभी implemented नहीं हैं। इन्हें अगली development phase में जोड़ना होगा। Team के ठीक 4 active members की validation अभी admin/model layer में पूरी तरह enforce नहीं है; tournament approve करने से पहले Super Admin manually verify करे।

## Safety & compliance
Platform independent community project है, Garena से affiliated नहीं। Garena trademark, game artwork, sounds या official branding बिना written permission इस्तेमाल न करें। इस version में player deposits, paid-entry, betting या wagering नहीं हैं। Commercial tournament संचालन, prize sponsorship और entry-fee policy से पहले भारत के लागू कानून, current rules, Garena permissions और tax obligations पर qualified legal advice लें।

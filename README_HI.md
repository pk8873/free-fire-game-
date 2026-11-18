# ROOM ARENA — Hindi Setup Guide

ROOM ARENA एक independent Django + PWA community tournament platform है। अभी format **Clash Squad 4v4** है।

## Player features

- Username, email, in-game name, unique Game UID और password से signup
- Login/logout, dashboard और player profile edit
- Squad create करना और invite code से join करना
- Active team roster देखना
- Captain दूसरे active member को captain बना सकता है
- Captain roster member remove कर सकता है और invite code बदल सकता है
- सामान्य member team छोड़ सकता है; captain को पहले captaincy transfer करनी होगी
- Pending/approved tournament registration के दौरान roster और invite code changes बंद रहते हैं
- Database rule एक player को एक समय में एक ही active squad में रहने देता है
- Tournament detail बिना login देख सकते हैं; registration केवल captain कर सकता है
- Clash Squad registration के लिए ठीक 4 active players जरूरी हैं

## Tournament और Admin features

- Super Admin players, teams, tournaments, registrations, matches, room credentials, results और disputes manage करता है
- Room ID/password release time से पहले छिपे रहते हैं
- Room details केवल approved tournament के assigned match participants को दिखते हैं
- Captain provisional result submit कर सकता है; Admin confirmation जरूरी है
- Approved participant match dispute भेज सकता है
- Dispute होने पर captain score edit नहीं कर सकता
- /health/ database connection check करता है

## Render पर Admin account — Shell access की जरूरत नहीं

पहला Super Admin web service startup पर environment variables से अपने आप बनाया जा सकता है। **Password को GitHub code में कभी न डालें।**

1. Render Dashboard में अपना ROOM ARENA Web Service खोलें।
2. Environment section खोलें।
3. ये तीन environment variables जोड़ें:
   - DJANGO_SUPERUSER_USERNAME = अपना चुना हुआ admin username
   - DJANGO_SUPERUSER_EMAIL = अपना admin email
   - DJANGO_SUPERUSER_PASSWORD = अपना मजबूत password, कम-से-कम 12 characters
4. Save changes करके redeploy करें।
5. Gunicorn start होते समय app उस username का superuser बनाएगा, अगर वह पहले से मौजूद नहीं है।
6. https://YOUR-SERVICE.onrender.com/admin/ खोलकर login करें।

इस प्रक्रिया में Render Shell या python manage.py createsuperuser चलाने की जरूरत नहीं है। यदि username पहले से मौजूद है तो code उसका password नहीं बदलेगा। Admin बन जाने के बाद चाहें तो DJANGO_SUPERUSER_PASSWORD variable हटा सकते हैं।

**ध्यान दें:** GitHub code hosting के secret variables अपने आप set नहीं कर सकता। Existing manually-created Render service में Environment page पर ये तीन values आपको एक बार डालनी होंगी। render.yaml Blueprint deploy में इन्हें secret prompts के रूप में शामिल करता है।

## Render settings

- Runtime: Python 3.12
- Build command: bash build.sh
- Start command: gunicorn config.wsgi:application
- SECRET_KEY: Render में generated long secret
- DEBUG: False
- ALLOWED_HOSTS: .onrender.com
- CSRF_TRUSTED_ORIGINS: https://*.onrender.com
- DATABASE_URL: PostgreSQL Internal Database URL

render.yaml /health/ health check configure करता है। PostgreSQL database अपने आप create नहीं होता; existing database का URL देना होगा।

## Windows पर local setup

    git clone https://github.com/pk8873/free-fire-game-.git
    cd free-fire-game-
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Home: http://127.0.0.1:8000/  
Admin: http://127.0.0.1:8000/admin/

## अभी बाकी features / limitations

- Automatic knockout bracket और match assignment
- Live game telemetry, automatic score verification, anti-cheat detection, Garena API
- Screenshot/evidence upload और automated referee system
- Email/SMS/push notifications (provider configuration बाकी)
- Email-based password reset (verified email setup बाकी)
- Payments, wallet, entry fees, betting या wagering जानबूझकर शामिल नहीं हैं
- High-load stress test, security audit और backup/restore testing बाकी हैं

Admin अभी registrations approve करता है, matches बनाता है, room details release करता है और results confirm करता है। Captain का submitted score Admin confirmation तक provisional रहता है।

## Legal / Rights

यह independent community platform है; Garena से affiliated या endorsed नहीं है। Garena logo, trademark, game art, audio या official assets permission के बिना उपयोग न करें। इस repository से tournament या commercial rights नहीं मिलते। Public/commercial launch, prize, sponsorship monetization या कोई fee लेने से पहले written permission/clarification और qualified Indian legal advice लें।

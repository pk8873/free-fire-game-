# ROOM ARENA — Hindi Setup Guide

ROOM ARENA एक independent Django + PWA community tournament platform है। अभी competition mode **Clash Squad 4v4** है।

## अभी उपलब्ध सुविधाएँ

### Player side
- Username, email, in-game name और unique Game UID से signup
- Login/logout और player dashboard
- Squad create करके invite code share करना
- Invite code से squad join करना (अधिकतम 4 active members)
- Published tournaments देखना
- Team captain द्वारा tournament registration request भेजना
- Registration status देखना: Pending / Approved / Rejected

### Admin / Tournament operations
- Super Admin tournament create/edit/publish कर सकता है
- Team registration approve/reject कर सकता है
- Match schedule और status manage कर सकता है
- Room ID/password और release time set कर सकता है
- Room credentials केवल approved match में शामिल team के logged-in members को release time के बाद दिखते हैं
- Team captain provisional match result submit/update कर सकता है
- Approved team का participant match dispute दर्ज कर सकता है
- Admin result confirm और dispute resolve कर सकता है

### Platform
- Responsive dark/orange interface
- PWA manifest और service worker
- Local SQLite, production PostgreSQL (DATABASE_URL)
- Committed database migrations
- Render deployment configuration

## Windows पर चलाएँ

Python 3.12 और Git install करें। PowerShell में:

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

## Render पर Deploy

1. Render Dashboard में PostgreSQL database बनाएँ और Internal Database URL copy करें।
2. GitHub से pk8873/free-fire-game- repository, branch main पर Web Service बनाएँ।
3. Runtime Python 3.12 रखें।
4. Build command: bash build.sh
5. Start command: gunicorn config.wsgi:application
6. Environment Variables:
   - SECRET_KEY = लंबी random secret value (या Render से generate करें)
   - DEBUG = False
   - ALLOWED_HOSTS = .onrender.com
   - CSRF_TRUSTED_ORIGINS = https://*.onrender.com
   - DATABASE_URL = PostgreSQL Internal Database URL
7. Deploy के बाद Render Shell में python manage.py createsuperuser चलाएँ।
8. अपने service URL के अंत में /admin/ खोलकर admin login करें।

render.yaml में DATABASE_URL manually देना होगा। Render के free plan, database retention और availability को अपने account में जाँचें।

## Admin को tournament चलाने का क्रम

1. /admin/ में Tournament बनाएँ और registration deadline/start time set करें।
2. Tournament status PUBLISHED करें।
3. Players signup करके teams बनाएँ; captain invite code team members को दे।
4. Captain के team में ठीक चार active players होने के बाद registration request भेजे।
5. Admin Registration को approve करे।
6. Admin Match बनाए और दोनों teams तथा schedule set करे।
7. Admin RoomCredential में room ID/password और release time भरे।
8. Match के बाद captain score submit करे; admin result verify करके CONFIRMED करे।
9. Dispute आने पर admin Match Dispute record review करके status/response update करे।

## अभी क्या नहीं है

Automated bracket, live scoring, notifications, proof/evidence upload, anti-cheat verification, Garena API, captain transfer, team member removal और payments अभी शामिल नहीं हैं। Admin को matches/approvals/room release/results manually manage करने होंगे। Match score user द्वारा submit होता है और admin confirmation तक provisional है।

इस session में Render deployment या production database migration run नहीं किया गया है। Deploy करने के बाद logs और workflows को test करना जरूरी है।

## Legal / Permission

यह independent community platform है, Garena से affiliated या endorsed नहीं है। Garena logo, trademark, game artwork, audio या official assets written permission के बिना उपयोग न करें। इस code से tournament या commercial rights नहीं मिलते। Public/commercial launch, prize, sponsorship monetization या कोई fee लेने से पहले written permission/clarification और qualified Indian legal advice लें।

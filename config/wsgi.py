import os
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Optional first-deploy admin bootstrap. Credentials are supplied only through
# hosting environment variables, never committed to source control.
logger = logging.getLogger(__name__)

def bootstrap_superuser():
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', '').strip()
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', '').strip()
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '')
    if not (username and email and password):
        return
    if len(password) < 12:
        logger.error('Admin bootstrap skipped: password must be at least 12 characters.')
        return
    try:
        from django.contrib.auth import get_user_model
        from django.db import IntegrityError, transaction
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            logger.info('Admin bootstrap: configured username already exists; no password changes made.')
            return
        try:
            with transaction.atomic():
                User.objects.create_superuser(username=username, email=email, password=password)
            logger.info('Admin bootstrap: initial superuser created.')
        except IntegrityError:
            logger.info('Admin bootstrap: another worker created the user first.')
    except Exception:
        logger.exception('Admin bootstrap could not complete; check database and environment settings.')

bootstrap_superuser()

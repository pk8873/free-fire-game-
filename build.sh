set -o errexit
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations players tournaments
python manage.py migrate
python manage.py collectstatic --no-input

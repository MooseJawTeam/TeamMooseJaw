set -e

echo 'Running startup.sh script'
cd django_app
pip install -r requirements.txt
python manage.py runserver
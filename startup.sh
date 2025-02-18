echo 'Running startup.sh script'
cd django_app
pip --root-user-action install -r requirements.txt
python manage.py runserver
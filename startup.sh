echo 'Running startup.sh script'
cd django_app
pip install --root-user-action ignore -r requirements.txt
python manage.py runserver $PORT
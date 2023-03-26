
python manage.py migrate --fake
python manage.py makemigrations
python manage.py migrate
gunicorn flashio.wsgi --bind=0.0.0.0:80
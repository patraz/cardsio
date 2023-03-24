python python manage.py flush --noinput
python manage.py migrate
gunicorn flashio.wsgi --bind=0.0.0.0:80
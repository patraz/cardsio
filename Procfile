
release: python manage.py makemigrations
release: python manage.py migrate
web: gunicorn flashio.wsgi --timeout 600

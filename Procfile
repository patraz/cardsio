release: python manage.py flush
release: python manage.py makemigrations
release: python manage.py migrate
web: gunicorn flashio.wsgi --timeout 600
release: celery -A flashio worker -l info -P gevent
release: celery -A flashio flower --port=5566
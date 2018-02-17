python manage,py migrate
gunicorn multiguru.wsgi:application -b :80 --reload

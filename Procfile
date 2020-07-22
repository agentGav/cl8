# TODO decide if it's better to call python python backend/manage.py instea
release: npm run build:django && cd backend && python manage.py collectstatic --no-input --clear && python manage.py migrate

web: cd backend && gunicorn config.wsgi:application
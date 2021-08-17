release: python backend/manage.py collectstatic --no-input --clear && python backend/manage.py migrate

web: gunicorn config.wsgi:application --chdir backend

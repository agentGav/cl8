# TODO: decide if it's better to call 'python backend/manage.py' instead
release: cd backend && python manage.py migrate

# TODO: it would be good to split the "build" steps from the "run" steps here
web: cp -R ./static-vue/ ./backend/static-vue/ && cd backend && python manage.py collectstatic --no-input --clear && gunicorn config.wsgi:application

justweb: cd backend && gunicorn config.wsgi:application

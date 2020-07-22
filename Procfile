# TODO decide if it's better to call python python backend/manage.py instea
release: cp ./static-vue/index.html ./backend/backend/templates/pages/vue.html && mv ./static-vue/ ./backend/backend/static-vue/ && cd backend && python manage.py collectstatic --no-input --clear && python manage.py migrate

web: cd backend && gunicorn config.wsgi:application
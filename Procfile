# TODO decide if it's better to call python python backend/manage.py instea
release: cd backend && python manage.py migrate

web: cp ./static-vue/index.html ./backend/backend/templates/pages/vue.html && rsync -vazuk ./static-vue/ ./backend/static-vue/ && cd backend && python manage.py collectstatic --no-input --clear && gunicorn config.wsgi:application
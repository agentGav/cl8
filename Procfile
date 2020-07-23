# TODO decide if it's better to call python python backend/manage.py instea
release: python manage.py migrate

web: cp ./static-vue/index.html ./backend/backend/templates/pages/vue.html && mv ./static-vue ./backend/static-vue && cd backend && python manage.py collectstatic --no-input --clear && cd backend && gunicorn config.wsgi:application
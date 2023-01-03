# just files are like makefiles but a bit
# more intuitive to use
# https://github.com/casey/just

@test *options:
    pipenv run pytest {{options}}

@ci:
    pipenv run pytest

@serve *options:
    python -m pipenv run python ./manage.py runserver {{options}}

@run *options:
    # run gunicorn in production
    python -m pipenv run gunicorn config.wsgi -b 0.0.0.0:9000 -t 300 {{options}}

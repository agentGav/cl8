# just files are like makefiles but a bit
# more intuitive to use
# https://github.com/casey/just

@test *options:
    python -m pipenv run pytest {{options}}

@install:
    #!/usr/bin/env sh
    python -m pipenv sync --help
    cd theme/static_src
    npm install --loglevel error

@ci:
    python -m pipenv run pytest

@serve *options:
    python -m pipenv run python ./manage.py runserver {{options}}

@manage *options:
    python -m pipenv run python ./manage.py {{options}}

@tailwind-dev:
    python -m pipenv run python ./manage.py tailwind start

@tailwind-build:
    python -m pipenv run python ./manage.py tailwind build

@run *options:
    # run gunicorn in production
    python -m pipenv run gunicorn config.wsgi -b 0.0.0.0:9000 -t 300 {{options}}



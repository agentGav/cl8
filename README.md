# Constellate - a shared address book for small groups

Constellate is an application designed to help communities of practice and othersmall-ish groups to discover skills and interests within the group to help with starting projects, finding help, or just deepening community engagement.



## Installation

Constellate is made of two parts - a django API in `backend`, and a VueJS front end in `cl8-web`.

If you have a recent version of python 3 (3.6 or higher), pipenv installed, and nodejs (10 or higher), and postgressql already on your machine, you should be able install all the dependencies with one command:

```
make install
```

### Installing the backend:

As mentione before the backend of Constellate is a Django project. We use pipenv on the project, although you can use regular pip if you prefer:

```
pipenv install
```

### Install the front end

The front end is a VueJS app:

```
npm install
```

You'll need them both running to develop the site, and a few environment variables set.

See env.sample for a full list of the required variables - we assume deployment to heroku, although this works anywhere that can run django apps.

## Usage

Once you have the necessary environment variables set, you can run the application locally with a single command.

```
make serve
```

This will:

- make a compiled version of the front end Vue JS application
- copy the main template to a directory where the django app can serve it
- copy accross any other front end assets generated as part of the build process
- serve the application on localhost, port 8000

You should be able to access the local instance of constellate by visiting:

http://localhost:8000


## Developing on constellate

Assuming you have the correct environment variables set, a dataabase setup, and installed the dependencies for javascript and python, you should be able to start development on the backend with

```
make dev.backend
```

This will setup a django dev server, that by default runs on port 8000.

You can do the same for the front end:

```
make dev.frontend
```

This will set up a hot reloading server, serving the vue front end http://127.0.0.1:8080, and proxying requests to the backend, to simulate the two services being run on a single machine in production.

### Running tests

The front end of constellate uses jest for tests. Calling `make test.frontend` uses the `vue-cli-service` to run tests with a special config.

```
make test.frontend
```

The backend of constellate uses pytest for testing the API. Call `make test.backend` to run pytest in the `backend` directory.

# Installation

Constellate is made of two parts - a django API in `backend`, and a VueJS front end in `cl8-web`.

You need them both running to develop the site.


### Setting up the django backend

While you almost definitely should be using postgres in development and production to to avoid surprises during deployment.

But you CAN use sqlite to spin up an instance and try it out. Pass in a databse url string like the one below:

```
DATABSE_URL="sqlite:///backend_db"
```

### Set up the front end

The front end is a Vuejs application, that talks to the backend. Like a lot of VueJS apps you can in stall using npm or yarn.

The examples below use npm for brevity.

```

npm install
```

Once you have that, for development call `npm run serve` - this sets up hot reloading, and development server:

```
npm run serve
```

To create a build for production `npm run build` creates an optimised version to deploy onto your choice of static hosting

```
npm run build
```
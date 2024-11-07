

heroku addons:create heroku-postgresql:hobby-dev --app cat-cl8
git remote add cat-cl8 https://git.heroku.com/cat-cl8.git
heroku config:push --file=.env.cat.prod --app cat-cl8
git push cat-cl8 ca-heroky-app:master
heroku buildpacks:add --index 1 heroku/nodejs -a cat-cl8
heroku buildpacks:add --index 2 heroku/python -a cat-cl8

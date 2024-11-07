#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

PG_USER=$PG_USER 
PG_PASSWORD=$PG_PASSWORD
HOST=localhost
DATABASE=cl8


# make a tiemstamped backup of the database, of the format cl8.YYYY-MM-DD--HH-MM.pgdump
# so you can restore with the command below, loading the backup file at cl8.YYYY-MM-DD--HH-MM.pgdump
# into the TARGET_DB_NAME
# pg_restore --clean --no-owner --no-privileges  -d TARGET_DB_NAME cl8.YYYY-MM-DD--HH-MM.pgdump
# 
PGUSER=$PG_USER PG_PASSWORD=$PG_PASSWORD pg_dump $DATABASE --no-owner --file=cl8.$(date +"%Y-%m-%d--%H-%M").pgdump --format=c
```




#!/bin/bash -e

CONTRIB_DIR=""
if [ -d /usr/share/postgresql/8.4/contrib ]; then
  CONTRIB_DIR="/usr/share/postgresql/8.4/contrib"
elif [ -d /usr/share/postgresql-8.3/contrib ]; then
  CONTRIB_DIR="/usr/share/postgresql-8.3/contrib"
else
  echo "!!! PostgreSQL contrib directory not found. Please edit"
  echo "!!! the database initialization script!"
  exit 1
fi

# Drop can fail if there is no database already defined
dropdb -U postgres nodewatcher || true
dropuser -U postgres nodewatcher || true
createuser -U postgres -S -D -R nodewatcher || true
createdb -U postgres -E UNICODE -T template0 -O nodewatcher nodewatcher
psql -U postgres nodewatcher -f ${CONTRIB_DIR}/ip4r.sql

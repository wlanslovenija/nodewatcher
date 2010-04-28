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

dropdb -U postgres wlanlj
createdb -U postgres -E UNICODE -O wlanlj wlanlj
psql -U postgres wlanlj -f ${CONTRIB_DIR}/ip4r.sql


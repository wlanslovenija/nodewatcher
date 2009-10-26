#!/bin/bash
dropdb -U postgres wlanlj
createdb -U postgres -E UNICODE -O wlanlj wlanlj
psql -U postgres wlanlj -f /usr/share/postgresql-8.3/contrib/ip4r.sql


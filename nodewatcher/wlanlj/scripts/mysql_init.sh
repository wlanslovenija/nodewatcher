#!/bin/bash -e

ROOT="root" # master user
SERVER="localhost" # MySQL server address
DATABASE="wlanlj" # database name 
USER=$DATABASE # database user name

echo "DROP DATABASE IF EXISTS ${DATABASE}; CREATE DATABASE ${DATABASE} CHARACTER SET utf8 COLLATE utf8_unicode_ci; GRANT ALL ON ${DATABASE}.* TO ${USER}@'%';" | mysql -h $SERVER -u $ROOT -p

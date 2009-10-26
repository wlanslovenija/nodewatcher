#!/usr/bin/python

# Setup import paths, since we are using Django models
import sys, os
sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wlanlj.settings'

# Imports
from django.db import connection, transaction
from django.conf import settings
import time

if len(sys.argv) != 2:
  print "Usage: %s dump" % sys.argv[0]
  exit(1)

def ensure_success(errcode):
  if errcode != 0:
    print "ERROR: Command failed to execute, aborting!"
    exit(1)

db_backend = settings.DATABASE_ENGINE
if settings.DATABASE_ENGINE.startswith('postgresql'):
  db_backend = 'postgresql'

if os.path.isfile('scripts/%s_init.sh' % db_backend):
  print "!!! NOTE: A setup script exists for your database. Be sure that it"
  print "!!! does what you want before continuing! You may have to edit the"
  print "!!! script and YOU MUST REVIEW IT! Otherwise the script may bork"
  print "!!! your installation. Press CTRL + C to abort now."

  try:
    time.sleep(5)
  except KeyboardInterrupt:
    exit(1)

  print ">>> Executing database setup script 'scripts/%s_init.sh'..." % db_backend
  ensure_success(os.system("scripts/%s_init.sh" % db_backend))
else:
  print "!!! NOTE: This script assumes that you have created and configured"
  print "!!! a proper database via settings.py! The database MUST be completely"
  print "!!! empty (no tables or sequences should be present). If this is not"
  print "!!! the case, this operation WILL FAIL! Press CTRL+C to abort now."
  
  if settings.DATABASE_ENGINE.startswith('postgresql'):
    print "!!!"
    print "!!! You are using a PostgreSQL database. Be sure that you have"
    print "!!! installed the IP4R extension or schema sync WILL FAIL!"
    print "!!! "
    print "!!! More information: http://ip4r.projects.postgresql.org"
    print "!!!"
  
  try:
    time.sleep(5)
  except KeyboardInterrupt:
    exit(1)

print ">>> Performing initial database sync..."
ensure_success(os.system("python manage.py syncdb --noinput"))

print ">>> Performing data cleanup..."
try:
  cursor = connection.cursor()
  cursor.execute("DELETE FROM auth_group_permissions")
  cursor.execute("DELETE FROM auth_group")
  cursor.execute("DELETE FROM auth_permission")
  cursor.execute("DELETE FROM auth_user")
  cursor.execute("DELETE FROM django_content_type")
  cursor.execute("DELETE FROM django_site")
  cursor.execute("DELETE FROM policy_trafficcontrolclass")
  transaction.commit_unless_managed()
except:
  print "ERROR: Data cleanup operation failed, aborting!"
  exit(1)

print ">>> Importing data from '%s'..." % sys.argv[1]
ensure_success(os.system("python manage.py loaddata %s" % sys.argv[1]))


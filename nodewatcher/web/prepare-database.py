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
os.system("python manage.py syncdb --noinput")

print ">>> Performing data cleanup..."
cursor = connection.cursor()
cursor.execute("DELETE FROM auth_group_permissions")
cursor.execute("DELETE FROM auth_group")
cursor.execute("DELETE FROM auth_permission")
cursor.execute("DELETE FROM auth_user")
cursor.execute("DELETE FROM django_content_type")
cursor.execute("DELETE FROM django_site")
cursor.execute("DELETE FROM policy_trafficcontrolclass")
transaction.commit_unless_managed()

print ">>> Importing data from '%s'..." % sys.argv[1]
os.system("python manage.py loaddata %s" % sys.argv[1])


#!/usr/bin/env python

# This script is used to sanitize daily database dump

# Setup import paths, since we are using Django models
import sys, os
sys.path.append('/var/www/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings_production'

# Imports
from django.core import serializers

if len(sys.argv) != 4:
  print "Usage: %s format input-file output-file" % sys.argv[0]
  exit(1)

if sys.argv[1] not in ('json', 'xml'):
  print "Invalid format '%s'! Valid formats are: json xml" % sys.argv[1]
  exit(1)

def object_transformator():
  # Read all objects one by one
  for holder in serializers.deserialize(sys.argv[1], open(sys.argv[2], 'r')):
    object = holder.object
    name = "%s.%s" % (object.__module__, object.__class__.__name__)
    
    # Some objects need to be sanitized
    if name == 'web.nodes.models.Node':
      if not object.is_dead():
        # We do not clean notes for dead nodes as they explain death background
        object.notes = ''
    elif name == 'web.account.models.UserAccount':
      object.vpn_password = 'XXX'
      object.name = ""
      object.phone = '5551234'
    elif name == 'django.contrib.auth.models.User':
      object.first_name = ""
      object.last_name = ""
      object.email = "user@example.com"
      object.password = '$1$1qL5F...$ZPQdHpHMsvNQGI4rIbAG70' # Password for all users is 123
    elif name == 'web.generator.models.Profile':
      object.root_pass = 'XXX'
    elif name == 'web.generator.models.StatsSolar':
      continue
    elif name == 'web.generator.models.WhitelistItem':
      continue
    elif name == 'django.contrib.sessions.models.Session':
      continue
    elif name == 'django.contrib.auth.models.Message':
      continue

    yield holder.object

# Write transformed objects out
out = open(sys.argv[3], 'w')
serializers.serialize(sys.argv[1], object_transformator(), stream = out)
out.close()

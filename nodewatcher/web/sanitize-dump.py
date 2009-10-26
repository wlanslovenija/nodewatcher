#!/usr/bin/python

# Setup import paths, since we are using Django models
import sys, os
sys.path.append('/var/www/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wlanlj.settings_production'

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
    name = holder.object.__class__.__name__
    object = holder.object
    
    # Some objects need to be sanitized
    if name == 'Node':
      object.notes = ''
    elif name == 'UserAccount':
      object.vpn_password = 'XXX'
      object.phone = '5551234'
    elif name == 'User':
      object.password = '$1$1qL5F...$ZPQdHpHMsvNQGI4rIbAG70'
    elif name == 'Profile':
      object.root_pass = 'XXX'
    elif name == 'StatsSolar':
      continue

    yield holder.object

# Write transformed objects out
out = open(sys.argv[3], 'w')
serializers.serialize(sys.argv[1], object_transformator(), stream = out)
out.close()


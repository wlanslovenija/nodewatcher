#!/usr/bin/python

# Setup import paths, since we are using Django models
import sys, os
sys.path.append('/var/www/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'web.settings_production'

# Import our models
from web.account.models import UserProfile
from django.contrib.auth.models import User
from django.db import transaction

@transaction.commit_manually
def authenticate_in_db(username, password):
  """
  Authenticates against the nodewatcher database.
  """
  try:
    user = User.objects.get(username = username)
    if user.get_profile().vpn_password == password:
      return True
  except User.DoesNotExist:
    return False
  except UserProfile.DoesNotExist:
    return False

f = open('/etc/openvpn/users.txt', 'r')
lines = f.read().split('\n')
f.close()

username = os.getenv('username')
password = os.getenv('password')

for line in lines:
  if not line:
    continue

  runame, rpass = line.split('\t')
  if username == runame and password == rpass:
    sys.exit(0)

# Try the database now
if authenticate_in_db(username, password):
  sys.exit(0)

sys.exit(1)

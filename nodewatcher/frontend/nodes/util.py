from django.conf import settings

# This will select the proper IP lookup mechanism, so it will also work on
# non-PostgreSQL databases (but it will be much slower for larger sets).
if 'postgresql' in settings.DATABASES['default']['ENGINE']:
  from frontend.nodes.util_postgresql import *
else:
  from frontend.nodes.util_dummy import *

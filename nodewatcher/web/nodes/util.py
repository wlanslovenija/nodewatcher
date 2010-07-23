from django.conf import settings

# This will select the proper IP lookup mechanism, so it will also work on
# non-PostgreSQL databases (but it will be much slower for larger sets).
if settings.DATABASES['default']['ENGINE'].find('postgresql') != -1:
  from web.nodes.util_postgresql import *
else:
  from web.nodes.util_dummy import *

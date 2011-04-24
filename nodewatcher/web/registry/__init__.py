from django.core import exceptions
from django.db import connection

from registry import rules as registry_rules

# Verify that we have full support for savepoints in the database backend
if not connection.features.uses_savepoints:
  raise exceptions.ImproperlyConfigured("Nodewatcher requires a database backend that supports transactional savepoints! We recommend you to use PostgreSQL.")


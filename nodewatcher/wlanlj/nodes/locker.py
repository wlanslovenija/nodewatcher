from django.db import connection, transaction
from django.conf import settings

#
# NOTE ABOUT LOCKING
#
# This function is needed to prevent concurrent access to
# data in sections that need to be serializable.  There is
# another option, namely to set transaction isolation level
# via SET TRANSACTION ISOLATION LEVEL SERIALIZABLE, but this
# has the drawback that it must be executed as the first
# query in a transaction (and we have no control over this,
# especially in Django).
#
# Therefore this method implements EXCLUSIVE table locks,
# currently only on PostgreSQL.
#

# Check for database drivers, this is not done in the decorator
# so this check is executed only once upon module load
if settings.DATABASE_ENGINE.startswith('postgresql'):
  LOCK_TYPE = "postgresql"
elif settings.DATABASE_ENGINE == 'mysql':
  LOCK_TYPE = "mysql"
else:
  LOCK_TYPE = None

def require_lock(*tables):
  def _lock(func):
    def _do_lock(*args,**kws):
      cursor = connection.cursor()

      if LOCK_TYPE == "postgresql":
        cursor.execute("LOCK TABLE %s IN ROW EXCLUSIVE MODE" % ', '.join(tables))
      elif LOCK_TYPE == "mysql":
        # Not yet implemented
        pass

      try:
        return func(*args,**kws)
      finally:
        if LOCK_TYPE == "mysql":
          # Not yet implemented
          pass
        
        if cursor:
          cursor.close()
    return _do_lock
  return _lock


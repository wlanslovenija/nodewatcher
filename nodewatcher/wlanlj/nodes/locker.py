from django.db import connection, transaction
from django.conf import settings

#
# NOTE ABOUT LOCKING
#
# This decorator is needed to prevent concurrent access to
# data in code sections that have to be serialized. One option
# is to set default isolation level of your database management
# system to SERIALIZABLE which has a performance drawback. There
# is another option, namely to set transaction isolation level
# at beginning of transaction via SET TRANSACTION ISOLATION
# LEVEL SERIALIZABLE or similar statement, but this is not
# possible in Django with TransactionMiddleware where transaction
# is opened at the start of a HTTP request.
#
# Therefore this method implements EXCLUSIVE table locks to
# acquire exclusive access for code sections where needed.
#

# Check for database drivers, this is not done in the decorator
# so this check is executed only once upon module load
if settings.DATABASE_ENGINE.startswith('postgresql'):
  # READ COMMITTED is the default isolation level in PostgreSQL so
  # we add explicit locking to support default isolation level.
  LOCK_TYPE = "postgresql"
elif settings.DATABASE_ENGINE.startswith('mysql'):
  # MySQL InnoDB default isolation level is REPEATABLE READ so we
  # add explicit locking to support default isolation level.
  LOCK_TYPE = "mysql"
elif settings.DATABASE_ENGINE.startswith('sqlite'):
  # Locking is not necessary for SQLite as default isolation
  # level for SQLite is SERIALIZABLE. (This means concurrent
  # transactions can fail and users have to retry their requests.)
  # You should probably add locking if you change isolation level.
  LOCK_TYPE = None
else:
  LOCK_TYPE = None

def require_lock(*tables):
  def _lock(func):
    def _do_lock(*args,**kws):
      cursor = connection.cursor()

      if LOCK_TYPE == "postgresql":
        cursor.execute("LOCK TABLES %s" % ', '.join(["%s WRITE" % x for x in tables]))
      elif LOCK_TYPE == "mysql":
        cursor.execute("LOCK TABLE %s IN ROW EXCLUSIVE MODE" % ', '.join(tables))

      try:
        return func(*args,**kws)
      finally:
        if LOCK_TYPE == "mysql":
          cursor.execute("UNLOCK TABLES")
        
        if cursor:
          cursor.close()
    return _do_lock
  return _lock

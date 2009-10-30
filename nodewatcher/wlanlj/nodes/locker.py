from django.db import connection, transaction

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

def require_lock(*tables):
  def _lock(func):
    def _do_lock(*args,**kws):
      cursor = connection.cursor()
      cursor.execute("LOCK TABLE %s IN ROW EXCLUSIVE MODE" % ', '.join(tables))

      try:
        return func(*args,**kws)
      finally:
        if cursor:
          cursor.close()
    return _do_lock
  return _lock


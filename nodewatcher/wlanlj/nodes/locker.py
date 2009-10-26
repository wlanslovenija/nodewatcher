from django.db import connection, transaction

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


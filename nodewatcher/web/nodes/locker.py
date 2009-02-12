from django.db import connection

def require_lock(*tables):
  def _lock(func):
    def _do_lock(*args,**kws):
      cursor = connection.cursor()
      cursor.execute("LOCK TABLES %s WRITE" %' '.join(tables))

      try:
        return func(*args,**kws)
      finally:
        cursor.execute("UNLOCK TABLES")
        if cursor:
          cursor.close()
    return _do_lock
  return _lock


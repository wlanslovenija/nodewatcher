from django.template import Library

register = Library()

def human_readable_kbytes(value):
  """
  Returns a properly formatted human readable bytes string.
  """
  if value > 1048576:
    return "%.02f GB" % (value / 1048576.0)
  elif value > 1024:
    return "%.02f MB" % (value / 1024.0)
  else:
    return "%.02f KB" % value

def time_delta(value):
  """
  Returns properly formatted time delta string.
  """
  days = hours = minutes = 0

  if value > 3600*24:
    days = value // (3600*24)
    value = value - days*3600*24

  if value > 3600:
    hours = value // 3600
    value = value - hours*3600

  if value > 60:
    minutes = value // 60
    value = value - minutes*60

  return "%02d d %02d h %02d min %02d sec" % (days, hours, minutes, value)

register.filter('human_readable_kbytes', human_readable_kbytes)
register.filter('time_delta', time_delta)


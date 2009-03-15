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

register.filter('human_readable_kbytes', human_readable_kbytes)

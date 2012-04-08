import socket
import urllib

from web.utils import ipaddr

class HttpTelemetryParseFailed(Exception):
  pass

class HttpTelemetryParser(object):
  """
  A simple class for obtaining nodewatcher telemetry in HTTP format.
  """
  def __init__(self, host, port):
    """
    Class constructor.
    
    @param host: Target host
    @param port: Target port
    """
    self.host = host
    self.port = port

  def parse_into(self, tree = None):
    """
    Fetches and parses data from the daemon via HTTP.

    @param tree: Target dictionary where data should be parsed into
    @return: Dictionary with parsed data
    """
    try:
      socket.setdefaulttimeout(15)
      data = urllib.urlopen("http://{host}:{port}/cgi-bin/nodewatcher".format(
        host = self.host, port = self.port)).read()
    except KeyboardInterrupt:
      raise
    except:
      raise HttpTelemetryParseFailed

    if tree is None:
      tree = {}

    for line in data.strip().split('\n'):
      # Skip all non machine-parsable comments
      line = line.strip()
      if line.startswith(';') or not line:
        continue

      # First colon splits the key and value parts
      try:
        key, value = line.split(':', 1)
        key = key.strip().split('.')
        value = value.strip()
      except ValueError:
        raise HttpTelemetryParseFailed

      reduce(lambda x, y: x.setdefault(y, x.__class__()), key[:-1], tree)[key[-1]] = value

    return tree

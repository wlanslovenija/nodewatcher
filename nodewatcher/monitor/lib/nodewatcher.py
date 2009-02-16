import urllib2

class NodeWatcher(object):
  """
  Parser for nodewatcher feeds from nodes.
  """
  @staticmethod
  def fetch(nodeIp):
    """
    Fetches node information via HTTP.
    """
    try:
      info = {}
      data = urllib2.urlopen('http://%s/cgi-bin/nodewatcher' % nodeIp).read()
      for line in data.split('\n'):
        if not line:
          break

        if line[0] == ';':
          continue

        key, value = line.split(':', 1)
        value = value.strip()
        key = key.split('.')

        d = info
        for part in key[:-1]:
          d = d.setdefault(part, {})
        
        d[key[-1]] = value
    except urllib2.URLError:
      return None

    return info
  
  @staticmethod
  def frequency_to_channel(frequency):
    """
    Converts a given frequency to a channel number.
    """
    try:
      frequency = float(frequency)
      if frequency < 10:
        frequency *= 1000

      channels = [2412, 2417, 2422, 2427, 2432, 2437, 2442, 2447, 2452, 2457, 2462, 2467, 2472, 2484]
      return channels.index(int(frequency)) + 1
    except:
      return 0


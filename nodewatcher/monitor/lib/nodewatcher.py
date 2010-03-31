# XXX Do NOT use urllib2 here as it causes memory leaks!
import urllib
import socket

# A flag that specifies when we should save fetched data for simulation purpuses
COLLECT_SIMULATION_DATA = False

def parse_node_info(data):
  """
  Parses node information into usable form.
  """
  try:
    info = {}
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
  except:
    return None

  return info

def fetch_node_info(node_ip):
  """
  Fetches node information via HTTP.
  """
  socket.setdefaulttimeout(15)
  try:
    data = urllib.urlopen('http://%s/cgi-bin/nodewatcher' % node_ip).read()
    if COLLECT_SIMULATION_DATA:
      try:
        f = open("simulator/data/nodes/%s.txt" % node_ip, 'w')
        f.write(data)
        f.close()
      except IOError:
        pass
    
    return parse_node_info(data)
  except:
    return None

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

def fetch_installed_packages(node_ip):
  """
  Fetches installed node packages.
  """
  socket.setdefaulttimeout(15)
  try:
    info = {}
    data = urllib.urlopen('http://%s/cgi-bin/opkgwatcher' % node_ip).read()
    for line in data.split('\n'):
      if not line:
        break
      
      package, x, version, y = line.strip().split(' ')
      info[package] = version
  except:
    return None

  return info


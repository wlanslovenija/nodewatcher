# XXX Do NOT use urllib2 here as it causes memory leaks!
import re
import urllib
import subprocess

# A flag that specifies when we should save fetched data for simulation purpuses
COLLECT_SIMULATION_DATA = False

class OlsrNode(object):
  """
  A simple class used for containing topology information received
  from the routing daemon.
  """
  ip = None
  links = None

  def __init__(self):
    self.links = []

def create_node(ip, nodes, hna):
  """
  Creates a new OlsrNode instance with specified parameters.
  """
  if not nodes.has_key(ip):
    node = OlsrNode()
    node.ip = ip
    nodes[ip] = node

    # Treat node entry as /32 HNA
    l = hna.setdefault(ip, [])
    l.append('%s/32' % ip)
  else:
    node = nodes[ip]

  return node

def parse_tables(data):
  """
  Parses the OLSR routing tables.
  """
  isTable = False
  isTableHead = False
  currentTable = ''

  nodes = {}
  hna = {}

  for line in data.splitlines():
    line = line.strip()
    if line[0:6] == 'Table:' and line[7:] in ('Topology', 'HNA', 'MID'):
      isTable = True
      isTableHead = True
      currentTable = line[7:]
      continue
    
    if isTable and isTableHead:
      isTableHead = False
      continue
    
    if isTable and not line:
      isTable = False
      currentTable = ''
      continue
    
    if currentTable == 'Topology':
      srcIp, dstIp, LQ, ILQ, ETX = line.split('\t')
      try:
        if not float(ETX):
          continue
      except ValueError:
        # Newer OLSR versions can use INFINITE as ETX
        continue

      srcNode = create_node(srcIp, nodes, hna)
      dstNode = create_node(dstIp, nodes, hna)

      srcNode.links.append((dstIp, LQ, ILQ, ETX))
    elif currentTable == 'HNA':
      try:
        network, cidr, gwIp = line.split('\t')
      except ValueError:
        # Newer OLSR versions have changed the format
        network, gwIp = line.split('\t')
        network, cidr = network.split('/')

      node = hna.setdefault(gwIp, [])
      node.append('%s/%s' % (network, cidr))
    elif currentTable == 'MID':
      ip, alias = line.split('\t')
      alias = alias.split(';')

      # Treat MIDs as /32 HNAs
      for x in alias:
        l = hna.setdefault(ip, [])
        l.append('%s/32' % x)
  
  return nodes, hna

def get_tables(olsr_ip = "127.0.0.1"):
  """
  Parses OLSR tables to extract topology and announce infos.

  @param olsr_ip: IP address of the router instance
  """
  try:
    data = urllib.urlopen('http://%s:2006' % olsr_ip).read()
    if COLLECT_SIMULATION_DATA:
      try:
        f = open("simulator/data/olsr.txt", 'w')
        f.write(data)
        f.close()
      except IOError:
        pass
    
    return parse_tables(data)
  except:
    return None

def parse_fping(data):
  """
  Parses fping results.
  """
  results = {}
  dupes = {}
  
  for line in data.splitlines():
    line = line.split()
    hostIp = line[0]
    up = False
    if not hostIp.startswith('10.'):
      continue
    
    if "duplicate" in line:
      dupes[hostIp] = True
      continue

    try:
      rcv = line[4].split('/')
      min, avg, max = line[7].split('/')
      loss = int(rcv[2].split('%')[0])
      results[hostIp] = (min, avg, max, loss)
    except:
      pass
  
  return (results, dupes)

def ping_hosts(count, hosts, packet_size = 56):
  """
  Pings specified hosts in parallel using fping.
  
  @param count: Number of ICMP ECHO packets to send
  @param hosts: A list of host IP addresses
  """
  if not hosts:
    return {}, {}
  
  # Spawn the fping process to ping hosts in parallel
  process = subprocess.Popen(
    ['/usr/sbin/fping', '-c', str(count), '-q', '-b%d' % packet_size] + hosts,
    stdout = subprocess.PIPE,
    stderr = subprocess.PIPE
  )
  
  # Parse results
  data = process.stderr.read()
  if COLLECT_SIMULATION_DATA:
    try:
      f = open("simulator/data/fping.txt", 'w')
      f.write(data)
      f.close()
    except IOError:
      pass
  
  return parse_fping(data)


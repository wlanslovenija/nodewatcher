import re
import urllib2
from popen2 import popen2 as popen

class OlsrNode(object):
  ip = None
  links = None

  def __init__(self):
    self.links = []

class OlsrParser(object):
  @staticmethod
  def createNode(ip, list, hna):
    if not list.has_key(ip):
      node = OlsrNode()
      node.ip = ip
      list[ip] = node

      # Treat node entry as /32 HNA
      l = hna.setdefault(ip, [])
      l.append('%s/32' % ip)
    else:
      node = list[ip]

    return node

  @staticmethod
  def getTables():
    try:
      response = urllib2.urlopen('http://127.0.0.1:2006')
    except:
      return None

    data = response.read()
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

        srcNode = OlsrParser.createNode(srcIp, nodes, hna)
        dstNode = OlsrParser.createNode(dstIp, nodes, hna)

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

        # Treat MIDs as /32 HNAs
        l = hna.setdefault(ip, [])
        l.append('%s/32' % alias)
    
    return nodes, hna

class PingParser(object):
  @staticmethod
  def pingHosts(count, hosts):
    results = {}
    dupes = {}

    if not hosts:
      return (results, dupes)
    
    rd, wr = popen("/usr/sbin/fping -c %d -q %s 2>&1" % (count, " ".join(hosts)))
    while True:
      line = rd.readline()
      if not line:
        break
      
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



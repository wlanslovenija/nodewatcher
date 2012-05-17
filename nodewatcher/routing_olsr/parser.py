import urllib

from nodewatcher.utils import ipaddr

class OlsrParseFailed(Exception):
  pass

class OlsrInfo(object):
  """
  A simple class for obtaining OLSR routing information from olsrd via
  mod-txtinfo plugin.
  """
  def __init__(self, host, port):
    """
    Class constructor.
    
    @param host: olsrd-mod-txtinfo host
    @param port: olsrd-mod-txtinfo port
    """
    self.host = host
    self.port = port
    self._tables = None
  
  def _fetch_data(self):
    """
    Fetches and parses data from the daemon via HTTP.
    """
    try:
      data = urllib.urlopen("http://{host}:{port}/".format(host = self.host,
        port = self.port)).read()
    except:
      raise OlsrParseFailed
    
    try:
      tables = data.split("Table: ")[1:]
      self._tables = {}
      for table in tables:
        table = table.strip().split('\n')
        self._tables[table[0].strip().lower()] = [tuple(x.strip().split("\t")) for x in table[2:]]
    except (ValueError, IndexError):
      raise OlsrParseFailed

  def get_topology(self):
    """
    Returns topology information.
    """
    if self._tables is None:
      self._fetch_data()
    
    # Parse topology information
    topology = {}
    for topo_entry in self._tables.get('topology', []):
      dst, src, lq, ilq, etx = topo_entry[:5]
      try:
        topology.setdefault(src, []).append({
          "dst" : ipaddr.IPAddress(dst),
          "lq"  : float(lq),
          "ilq" : float(ilq),
          "etx" : float(etx),
        })
      except ValueError:
        # Skip entries with INFINITE ETX value
        continue
    
    return topology
  
  def get_announces(self):
    """
    Returns node announces information.
    """
    if self._tables is None:
      self._fetch_data()
    
    # Parse announced subnets information
    announces = {}
    for hna_entry in self._tables.get('hna', []):
      net, router_id = hna_entry[:2]
      announces.setdefault(router_id, []).append({
        "net" : ipaddr.IPNetwork(net),
      })
    
    return announces

  def get_aliases(self):
    """
    Returns node announces information.
    """
    if self._tables is None:
      self._fetch_data()
    
    # Parse router aliases information
    aliases = {}
    for mid_entry in self._tables.get('mid', []):
      router_id, alias = mid_entry[:2]
      tmp = aliases.setdefault(router_id, [])
      tmp += [
        { "alias" : ipaddr.IPAddress(x) }
        for x in alias.split(';')
      ]
    
    return aliases


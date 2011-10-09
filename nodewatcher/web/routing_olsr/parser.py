import urllib

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
    
    # TODO Parse topology information
    # self._tables['topology']
    pass
  
  def get_announces(self):
    """
    Returns node announces information.
    """
    if self._tables is None:
      self._fetch_data()
    
    # TODO
    # self._tables['hna']
    pass

  def get_aliases(self):
    """
    Returns node announces information.
    """
    if self._tables is None:
      self._fetch_data()
    
    # TODO
    # self._tables['mid']
    pass


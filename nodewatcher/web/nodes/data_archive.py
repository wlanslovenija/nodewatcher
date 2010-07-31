from django.conf import settings
from datetime import datetime

if getattr(settings, 'DATA_ARCHIVE_ENABLED', False):
  # Only do this if data archival is enabled
  import pymongo
  
  # Ensure there is a connection to MongoDB
  connection = pymongo.Connection(
    settings.DATA_ARCHIVE_HOST,
    settings.DATA_ARCHIVE_PORT
  )
  
  # Get proper database handle
  db = getattr(connection, settings.DATA_ARCHIVE_DB)
  
  # Ensure indices on graph and timestamp for statistics collection
  db.statistics.ensure_index([('graph', pymongo.ASCENDING), ('timestamp', pymongo.ASCENDING)])
  
  # Ensure indices on snapshot and uuid for topology archive
  db.topology.ensure_index([('snapshot_id', pymongo.ASCENDING), ('node.uuid', pymongo.ASCENDING)])
  
  def record_data(graph, timestamp, data):
    """
    Records graph data into the archive.
    
    @param graph: Graph identifier
    @param timestamp: Timestamp
    @param data: Data dictionary
    """
    if timestamp > datetime.now():
      return
    
    if all([x == "NaN" or x == None for x in data.values()]):
      return
    
    q = {
      'graph' : graph,
      'timestamp' : timestamp
    }
    
    data.update(q)
    db.statistics.update(q, data, upsert = True)
  
  def fetch_data(graph, start = None, sort = False):
    """
    Returns all data records recorded for a specific graph.
    
    @param graph: Graph identifier
    @param start: Start datetime
    @param sort: Should results be sorted by timestamp
    @return: A list of data items
    """
    if sort:
      sort = [('timestamp', pymongo.ASCENDING)]
    else:
      sort = None
    
    query = { 'graph' : graph }
    if start is not None:
      query.update({ 'timestamp' : { '$gt' : start }})
    
    return db.statistics.find(query, sort = sort)
  
  def record_topology_entry(snapshot_id, timestamp, node, links):
    """
    Archives a topology entry for a node.
    
    @param snapshot_id: Unique snapshot identifier
    @param timestamp: A datetime timestamp object
    @param node: Node instance
    @param links: A list of Link instances
    """
    db.topology.insert({
      'snapshot_id' : snapshot_id,
      'timestamp'   : timestamp,
      'node' : {
        'uuid'  : node.uuid,
        'name'  : node.name,
        'ip'    : node.ip,
        'type'  : node.node_type
      },
      'links' : [
        {
          'peer_uuid' : link.dst.uuid,
          'lq'        : link.lq,
          'ilq'       : link.ilq,
          'etx'       : link.etx
        } for link in links
      ]
    })
else:
  # Define stub functions that do nothing at all
  def record_data(graph, timestamp, data):
    pass
  
  def fetch_data(graph, start = None, sort = False):
    return []
  
  def record_topology_entry(snapshot_id, timestamp, node, links):
    pass


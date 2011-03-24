import os
import time
import traceback

from celery.decorators import task as celery_task
from celery.log import get_task_logger

from django.conf import settings
from django.core.cache import cache

from web.nodes import models as nodes_models
from web.monitor import rrd, graphs

# XXX These graphs are currently hardcoded and should be removed on graph API refactor
GLOBAL_GRAPHS = {
  -1 : (rrd.RRANodesByStatus, 'Nodes By Status',          'global_nodes_by_status.rrd'),
  -2 : (rrd.RRAGlobalClients, 'Global Connected Clients', 'global_client_count.rrd'),
}

@celery_task()
def draw_graph(graph_id, timespan):
  """
  Draws the specified graph.
  
  @param graph_id: Graph primary key
  @param timespan: Timespan to draw the graph for
  @return: True on success, False on failure
  """
  logger = draw_graph.get_logger()
  
  # First check that we haven't drawn this graph already
  result = cache.get('nodewatcher.graphs.drawn.{0}.{1}'.format(graph_id, timespan))
  if result is not None:
    return bool(result)
  
  # Since the graph has not yet been drawn, let's draw it
  try:
    graph_id = int(graph_id)
    # XXX Check for hardcoded graphs 
    if graph_id > 0:
      graph = nodes_models.GraphItem.objects.get(pk = graph_id)
      archive_path = str(os.path.join(settings.MONITOR_WORKDIR, 'rra', graph.rra))
      
      # Actually draw the graph
      rrd.RRA.graph(
        graphs.RRA_CONF_MAP[graph.type],
        str(graph.title),
        graph.id,
        archive_path,
        end_time = int(time.mktime(graph.last_update.timetuple())),
        dead = graph.dead,
        last_update = graph.last_update,
        timespan = timespan
      )
    else:
      # XXX One of the hardcoded graphs
      conf, title, rrd_path = GLOBAL_GRAPHS[graph_id]
      archive_path = str(os.path.join(settings.MONITOR_WORKDIR, 'rra', rrd_path))
      
      # Actually draw the graph
      rrd.RRA.graph(conf, title, graph_id, archive_path, timespan = timespan)
    
    result = True
  except:
    logger.error(traceback.format_exc())
    result = False
  
  # Mark the graph as drawn
  cache.set('nodewatcher.graphs.drawn.{0}.{1}'.format(graph_id, timespan), result)
  return result

def defer_draw_graph(graph_id, timespan, publisher = None):
  """
  Makes a deferred call for drawing a graph, but checking the cache
  first to see if an actual call is needed.
  
  @param graph_id: Graph primary key
  @param timespan: Timespan to draw the graph for
  @param publisher: Celery publisher to use for dispatching tasks
  """
  if not cache.get('nodewatcher.graphs.drawn.{0}.{1}'.format(graph_id, timespan)):
    return draw_graph.apply_async(args = [graph_id, timespan], publisher = publisher)

def get_publisher():
  """
  Returns the Celery publisher.
  """
  return draw_graph.get_publisher()


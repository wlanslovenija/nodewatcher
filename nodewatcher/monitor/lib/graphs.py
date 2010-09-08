from django.conf import settings
from web.nodes.models import GraphItem, GraphType
from lib.rra import *
from datetime import datetime, timedelta
from traceback import format_exc
import logging
import os
import time

# Mapping of graph types to their respective rrd configurations
RRA_CONF_MAP = {
  GraphType.RTT             : RRARTT,
  GraphType.LQ              : RRALinkQuality,
  GraphType.Clients         : RRAClients,
  GraphType.Traffic         : RRAIface,
  GraphType.LoadAverage     : RRALoadAverage,
  GraphType.NumProc         : RRANumProc,
  GraphType.MemUsage        : RRAMemUsage,
  GraphType.Solar           : RRASolar,
  GraphType.WifiCells       : RRAWifiCells,
  GraphType.OlsrPeers       : RRAOlsrPeers,
  GraphType.PacketLoss      : RRAPacketLoss,
  GraphType.WifiBitrate     : RRAWifiBitrate,
  GraphType.WifiSignalNoise : RRAWifiSignalNoise,
  GraphType.WifiSNR         : RRAWifiSNR,
  GraphType.ETX             : RRAETX,
  GraphType.Temperature     : RRATemperature
}

class Grapher(object):
  """
  A helper class used to dispatch graph requests to rrdtool and
  the archiver (when enabled).
  """
  def __init__(self, node):
    """
    Class constructor.
    
    @param node: A valid Node instance
    """
    self.node = node
    self.rebooted = False
  
  def enable_reboot_mode(self, uptime, last_seen):
    """
    Call this when the node in question has been rebooted to properly
    handle counter datasources.
    
    @param uptime: New node uptime
    @param last_seen: Old last seen value
    """
    self.rebooted = True
    
    # Ensure that we don't go too far back with our uptime as this could
    # cause RRD update problems
    self.uptime = min((datetime.now() - last_seen).seconds - 10, uptime)
  
  def add_graph(self, type, title, filename, *values, **attrs):
    """
    A helper function for generating graphs.
    """
    if getattr(settings, 'MONITOR_DISABLE_GRAPHS', None):
      return
    
    # Get optional name parameter
    name = attrs.get('name', '')
    
    # Get parent instance (toplevel by default)
    parent = attrs.get('parent', None)
    graph_image_name = '%s_%s.png' % (filename, self.node.pk)
    graph_rra_name = '%s_%s.rrd' % (filename, self.node.pk)
    
    # Resolve graph configuration
    conf = RRA_CONF_MAP[type]
    
    # Resolve graph ordering
    display_priority = GraphType.ordering.index(type)

    try:
      graph = GraphItem.objects.get(node = self.node, name = name, type = type, parent = parent)
      if graph.graph != graph_image_name:
        graph.graph = graph_image_name
    except GraphItem.DoesNotExist:
      graph = GraphItem(node = self.node, name = name, type = type, parent = parent)
      graph.rra = graph_rra_name
      graph.graph = graph_image_name
    
    rra = str(os.path.join(settings.MONITOR_WORKDIR, 'rra', graph.rra))
    try:
      # In reboot mode we insert some values before the current entry so
      # spikes are avoided
      if self.rebooted and any([x.is_counter() for x in conf.sources]):
        ts = int(time.time() - self.uptime)
        RRA.update(self.node, conf, rra, *[None for x in values], graph = graph.pk, timestamp = ts - 1)
        RRA.update(self.node, conf, rra, *[0 for x in values], graph = graph.pk, timestamp = ts)
      
      # Update the entry
      RRA.update(
        self.node,
        conf,
        rra,
        *values,
        graph = graph.pk
      )
    except:
      logging.warning(format_exc())
    
    graph.title = title
    graph.last_update = datetime.now()
    graph.dead = False
    graph.need_redraw = True
    graph.display_priority = display_priority
    graph.save()
    return graph


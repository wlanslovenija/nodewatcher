from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from web.core import models as core_models
from web.core.monitor import processors as monitor_processors
from web.nodes import models as nodes_models
from web.routing_olsr import parser as olsr_parser
from web.registry import fields as registry_fields
from web.registry import registration

class OlsrRoutingTopologyMonitor(core_models.RoutingTopologyMonitor):
  """
  OLSR routing topology.
  """
  pass

registration.point("node.monitoring").register_item(OlsrRoutingTopologyMonitor)

class OlsrTopologyLink(core_models.TopologyLink):
  """
  OLSR topology link.
  """
  lq = models.FloatField(default = 0.0)
  ilq = models.FloatField(default = 0.0)
  etx = models.FloatField(default = 0.0)

class OlsrRoutingAnnounceMonitor(core_models.RoutingAnnounceMonitor):
  """
  OLSR network announces.
  """
  pass

registration.point("node.monitoring").register_item(OlsrRoutingAnnounceMonitor)

class OlsrFetchProcessor(monitor_processors.MonitoringProcessor):
  """
  Processor that handles monitoring of olsrd routing daemon.
  """
  def preprocess(self, context, nodes):
    """
    Invoked before processing specific nodes and should select the nodes
    that will be processed.
    
    @param context: Current context
    @param nodes: A list of nodes that are to be processed
    @return: A (possibly) modified context and a (possibly) filtered list of nodes
    """
    with context.in_namespace("routing"):
      with context.in_namespace("olsr"):
        self.logger.info("Parsing olsrd information...")
        olsr_info = olsr_parser.OlsrInfo(host = settings.OLSRD_MONITOR_HOST,
          port = settings.OLSRD_MONITOR_PORT)
        
        try:
          context.topology = olsr_info.get_topology()
          context.announces = olsr_info.get_announces()
          context.aliases = olsr_info.get_aliases()
        except olsr_parser.OlsrParseFailed:
          self.logger.warning("Failed to parse olsrd feeds!")
          raise
        
        # Create a mapping from router ids to nodes
        self.logger.info("Mapping router IDs to node instances...")
        visible_routers = set(context.topology.keys())
        registered_routers = set()
        context.router_id_map = {}
        for node in nodes_models.Node.objects.regpoint("config").registry_fields( \
          router_id = "RouterIdConfig.router_id").filter(routeridconfig_family = "ipv4"):
          context.router_id_map[node.router_id] = node
          registered_routers.add(node.router_id)
        
        self.logger.info("Creating unknown node instances...")
        for router_id in visible_routers.difference(registered_routers):
          # Create an invalid node for each unknown router id seen by olsrd
          node = nodes_models.Node()
          node.save()
          nodes.append(node)
          context.router_id_map[router_id] = node
          
          rid_cfg = node.config.core.routerid(create = core_models.RouterIdConfig)
          rid_cfg.router_id = router_id
          rid_cfg.family = "ipv4"
          rid_cfg.save()
          
          status_mon = node.monitoring.core.status(create = core_models.StatusMonitor)
          status_mon.status = "invalid"
          status_mon.save()
    
    return context, nodes
  
  def process_first_pass(self, context, node):
    """
    Called for every processed node in the first pass. Should fetch and store
    data for the second pass.
    
    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    try:
      router_id = node.config.core.routerid(queryset = True).get(family = "ipv4")
      topology = context.routing.olsr.topology.get(router_id, [])
      announces = context.routing.olsr.announces.get(router_id, [])
      aliases = context.routing.olsr.aliases.get(router_id, [])
      
      # Setup links in topology tables
      try:
        rtm = node.monitoring.network.topology(onlyclass = OlsrRoutingTopologyMonitor)[0]
        existing_links = set(rtm.links.all())
      except IndexError:
        rtm = node.monitoring.network.topology(create = OlsrRoutingTopologyMonitor)
        rtm.save()
        existing_links = set()
      
      for link in topology:
        dst_node = context.routing.olsr.router_id_map.get(link['dst'], None)
        if not dst_node:
          # XXX How should this be handled? Inconsistency in topology table???
          continue
        
        for elink in existing_links.copy():
          if elink.peer == dst_node:
            existing_links.remove(elink)
            break
        else:
          elink = OlsrTopologyLink(monitor = rtm, peer = dst_node)
        
        elink.lq = link['lq']
        elink.ilq = link['ilq']
        elink.etx = link['etx']
        elink.save()
      
      # Remove all links that do not exist anymore
      for link in existing_links:
        link.delete()
      
      # Setup networks in announce tables
      existing_announces = node.monitoring.network.announces(onlyclass = OlsrRoutingAnnounceMonitor)
      for announce in announces + aliases:
        network = announce['net'] if 'net' in announce else announce['alias']
        for eannounce in existing_announces.copy():
          if eannounce.network == network:
            existing_announces.remove(eannounce)
            break
        else:
          eannounce = OlsrRoutingAnnounceMonitor(root = node, network = network)
        
        eannounce.status = "ok" if 'net' in announce else "alias"
        eannounce.save()
      
      # Remove all announces that do not exist anymore
      for announce in existing_announces:
        announce.delete()
    except core_models.RouterIdConfig.DoesNotExist:
      # No router-id for this node can be found for IPv4; this means
      # that we have nothing to do here
      pass
    
    return context

monitor_processors.register_processor(OlsrFetchProcessor)


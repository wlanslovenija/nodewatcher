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

class OlsrFetchProcessor(monitor_processors.MonitoringProcessor):
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
        olsr_info = olsr_parser.OlsrInfo(host = settings.OLSRD_MONITOR_HOST,
          port = settings.OLSRD_MONITOR_PORT)
        
        try:
          context.topology = olsr_info.get_topology()
          context.announces = olsr_info.get_announces()
          context.aliases = olsr_info.get_aliases()
        except olsr_parser.OlsrParseFailed:
          # TODO emit a global warning somewhere?
          pass
        
        # Create nodes that are visible but not registered as invalid
        visible_routers = set(context.topology.keys())
        registered_routers = nodes_models.Node.objects.regpoint("config").registry_fields(
          router_id = "RouterIdConfig.router_id",
        ).filter(routeridconfig_family = "ipv4").values_list("router_id", flat = True)
        
        for router_id in visible_routers.difference(registered_routers):
          # TODO Create this node and mark it as an invalid node
          pass
    
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
      
      # TODO populate monitoring registry
    except core_models.RouterIdConfig.DoesNotExist:
      # No router-id for this node can be found for IPv4; this means
      # that we have nothing to do here
      pass
    
    return context

monitor_processors.register_processor(OlsrFetchProcessor)


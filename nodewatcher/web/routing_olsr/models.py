from django.db import models

from web.core import models as core_models
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

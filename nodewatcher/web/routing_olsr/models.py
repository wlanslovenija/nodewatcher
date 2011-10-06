from django.db import models
from django.utils.translation import ugettext as _

from web.core import models as core_models
from web.nodes import models as nodes_models
from web.registry import fields as registry_fields
from web.registry import registration

class OlsrRoutingTopologyMonitor(RoutingTopologyMonitor):
  """
  OLSR routing topology.
  """
  pass

registration.point("node.monitoring").register_item(OlsrRoutingTopologyMonitor)

class OlsrTopologyLink(models.Model):
  """
  OLSR topology link.
  """
  monitor = models.ForeignKey(OlsrRoutingTopologyMonitor, related_name = 'peers_olsr')
  peer = models.ForeignKey(nodes_models.Node, related_name = 'peers_olsr')
  lq = models.FloatField(default = 0.0)
  ilq = models.FloatField(default = 0.0)
  etx = models.FloatField(default = 0.0)


from django.db import models
from django.utils.translation import ugettext as _

from web.nodes import models as nodes_models
from web.registry import fields as registry_fields
from web.registry import registration

class GeneralMonitor(registration.bases.NodeMonitoringRegistryItem):
  """
  General monitored parameters about a node.
  """
  first_seen = models.DateTimeField(null = True)
  last_seen = models.DateTimeField(null = True)
  uptime = models.IntegerField(null = True)
  
  class Meta:
    app_label = "core"
  
  class RegistryMeta:
    registry_id = "core.general"

registration.point("node.monitoring").register_item(GeneralMonitor)

class StatusMonitor(registration.bases.NodeMonitoringRegistryItem):
  """
  Node's status.
  """
  status = registry_fields.SelectorKeyField("node.monitoring", "core.status#status")
  has_warnings = models.BooleanField(default = False)
  
  class Meta:
    app_label = "core"
  
  class RegistryMeta:
    registry_id = "core.status"

registration.point("node.monitoring").register_choice("core.status#status", "up", _("Up"))
registration.point("node.monitoring").register_choice("core.status#status", "down", _("Down"))
registration.point("node.monitoring").register_choice("core.status#status", "invalid", _("Invalid"))
registration.point("node.monitoring").register_choice("core.status#status", "visible", _("Visible"))
registration.point("node.monitoring").register_choice("core.status#status", "pending", _("Pending"))
registration.point("node.monitoring").register_item(StatusMonitor)

class RoutingTopologyMonitor(registration.bases.NodeMonitoringRegistryItem):
  """
  Routing topology.
  """
  peers_count = models.IntegerField(default = 0)
  
  class Meta:
    app_label = "core"
  
  class RegistryMeta:
    registry_id = "network.routing.topology"
    multiple = True

registration.point("node.monitoring").register_item(RoutingTopologyMonitor)

class TopologyLink(models.Model):
  """
  Generic topology link not associated with any specific routing protocol.
  """
  monitor = models.ForeignKey(RoutingTopologyMonitor, related_name = 'peers')
  peer = models.ForeignKey(nodes_models.Node, related_name = 'peers_generic')
  
  class Meta:
    app_label = "core"


import polymorphic

from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher import datastream
from nodewatcher.nodes import models as nodes_models
from nodewatcher.registry import fields as registry_fields
from nodewatcher.registry import registration

class GeneralMonitor(registration.bases.NodeMonitoringRegistryItem):
  """
  General monitored parameters about a node.
  """
  first_seen = models.DateTimeField(null = True)
  last_seen = models.DateTimeField(null = True)
  
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
  class Meta:
    app_label = "core"
  
  class RegistryMeta:
    registry_id = "network.routing.topology"
    multiple = True

registration.point("node.monitoring").register_item(RoutingTopologyMonitor)

class TopologyLink(polymorphic.PolymorphicModel):
  """
  Generic topology link not associated with any specific routing protocol.
  """
  monitor = models.ForeignKey(RoutingTopologyMonitor, related_name = 'links')
  peer = models.ForeignKey(nodes_models.Node, related_name = 'links')
  last_seen = models.DateTimeField()
  
  class Meta:
    app_label = "core"

class RoutingAnnounceMonitor(registration.bases.NodeMonitoringRegistryItem):
  """
  Node's announced networks.
  """
  network = registry_fields.IPAddressField()
  status = registry_fields.SelectorKeyField("node.monitoring", "network.routing.announces#status")
  last_seen = models.DateTimeField()
  
  class Meta:
    app_label = "core"
  
  class RegistryMeta:
    registry_id = "network.routing.announces"
    multiple = True

registration.point("node.monitoring").register_choice("network.routing.announces#status", "ok", _("Ok"))
registration.point("node.monitoring").register_choice("network.routing.announces#status", "alias", _("Alias"))
registration.point("node.monitoring").register_choice("network.routing.announces#status", "unallocated", _("Unallocated"))
registration.point("node.monitoring").register_choice("network.routing.announces#status", "conflicting", _("Conflicting"))
registration.point("node.monitoring").register_item(RoutingAnnounceMonitor)

class SystemStatusMonitor(registration.bases.NodeMonitoringRegistryItem):
  """
  Basic system status information like uptime and the local time.
  """
  uptime = models.PositiveIntegerField()
  local_time = models.DateTimeField()

  connect_datastream = datastream.ConnectDatastream(
    uptime = datastream.IntegerField()
  )

  class Meta:
    app_label = "core"

  class RegistryMeta:
    registry_id = "system.status"

registration.point("node.monitoring").register_item(SystemStatusMonitor)

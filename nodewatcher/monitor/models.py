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

class GeneralResourcesMonitor(registration.bases.NodeMonitoringRegistryItem):
  """
  General resources such as load average, system memory and the number of processes.
  """
  loadavg_1min = models.FloatField()
  loadavg_5min = models.FloatField()
  loadavg_15min = models.FloatField()
  memory_free = models.PositiveIntegerField()
  memory_buffers = models.PositiveIntegerField()
  memory_cache = models.PositiveIntegerField()
  processes = models.PositiveIntegerField()

  connect_datastream = datastream.ConnectDatastream(
    loadavg_1min = datastream.FloatField(),
    loadavg_5min = datastream.FloatField(),
    loadavg_15min = datastream.FloatField(),
    memory_free = datastream.IntegerField(),
    memory_buffers = datastream.IntegerField(),
    memory_cache = datastream.IntegerField(),
    processes = datastream.IntegerField()
  )

  class RegistryMeta:
    registry_id = "system.resources.general"

registration.point("node.monitoring").register_item(GeneralResourcesMonitor)

class NetworkResourcesMonitor(registration.bases.NodeMonitoringRegistryItem):
  """
  Network resources such as number of routes and number of tracked TCP and UDP
  connections.
  """
  routes = models.IntegerField()
  tcp_connections = models.IntegerField()
  udp_connections = models.IntegerField()

  connect_datastream = datastream.ConnectDatastream(
    routes = datastream.IntegerField(),
    tcp_connections = datastream.IntegerField(),
    udp_connections = datastream.IntegerField()
  )

  class RegistryMeta:
    registry_id = "system.resources.network"

registration.point("node.monitoring").register_item(NetworkResourcesMonitor)

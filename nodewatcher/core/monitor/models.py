import polymorphic

from django.db import models
from django.utils.translation import ugettext as _

from .. import models as core_models
from ..registry import fields as registry_fields
from ..registry import registration

# Creates monitoring registration point
registration.create_point(core_models.Node, 'monitoring')


class GeneralMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    General monitored parameters about a node.
    """

    first_seen = models.DateTimeField(null=True)
    last_seen = models.DateTimeField(null=True)

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        registry_id = 'core.general'

registration.point('node.monitoring').register_item(GeneralMonitor)


class CgmGeneralMonitor(GeneralMonitor):
    """
    General monitored parameters about a node that has firmware generated
    by the CGMs.
    """

    uuid = models.CharField(max_length=40, null=True)
    firmware = models.CharField(max_length=100, null=True)

    class RegistryMeta(GeneralMonitor.RegistryMeta):
        pass

registration.point('node.monitoring').register_item(CgmGeneralMonitor)


class StatusMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Node's status.
    """

    status = registry_fields.SelectorKeyField('node.monitoring', 'core.status#status')
    has_warnings = models.BooleanField(default=False)

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        registry_id = 'core.status'

# TODO: This should not be hard-coded? Should be moved to modules?
registration.point('node.monitoring').register_choice('core.status#status', 'up', _("Up"))
registration.point('node.monitoring').register_choice('core.status#status', 'down', _("Down"))
registration.point('node.monitoring').register_choice('core.status#status', 'invalid', _("Invalid"))
registration.point('node.monitoring').register_choice('core.status#status', 'visible', _("Visible"))
registration.point('node.monitoring').register_choice('core.status#status', 'pending', _("Pending"))
registration.point('node.monitoring').register_item(StatusMonitor)


class RoutingTopologyMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Routing topology.
    """

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        registry_id = 'network.routing.topology'
        multiple = True

registration.point('node.monitoring').register_item(RoutingTopologyMonitor)


class TopologyLink(polymorphic.PolymorphicModel):
    """
    Generic topology link not associated with any specific routing protocol.
    """

    monitor = models.ForeignKey(RoutingTopologyMonitor, related_name='links')
    peer = models.ForeignKey(core_models.Node, related_name='links')
    last_seen = models.DateTimeField()

    class Meta:
        app_label = 'core'


class RoutingAnnounceMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Node's announced networks.
    """

    network = registry_fields.IPAddressField()
    status = registry_fields.SelectorKeyField('node.monitoring', 'network.routing.announces#status')
    last_seen = models.DateTimeField()

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        registry_id = 'network.routing.announces'
        multiple = True

# TODO: Does this depend on routing protocol?
registration.point('node.monitoring').register_choice('network.routing.announces#status', 'ok', _("Ok"))
registration.point('node.monitoring').register_choice('network.routing.announces#status', 'alias', _("Alias"))
registration.point('node.monitoring').register_choice('network.routing.announces#status', 'unallocated', _("Unallocated"))
registration.point('node.monitoring').register_choice('network.routing.announces#status', 'conflicting', _("Conflicting"))
registration.point('node.monitoring').register_item(RoutingAnnounceMonitor)


class SystemStatusMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Basic system status information like uptime and the local time.
    """

    uptime = models.PositiveIntegerField()
    local_time = models.DateTimeField()

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        registry_id = 'system.status'

registration.point('node.monitoring').register_item(SystemStatusMonitor)


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

    class RegistryMeta:
        registry_id = 'system.resources.general'

registration.point('node.monitoring').register_item(GeneralResourcesMonitor)


class NetworkResourcesMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Network resources such as number of routes and number of tracked TCP and UDP
    connections.
    """

    routes = models.IntegerField()
    tcp_connections = models.IntegerField()
    udp_connections = models.IntegerField()

    class RegistryMeta:
        registry_id = 'system.resources.network'

registration.point('node.monitoring').register_item(NetworkResourcesMonitor)


class InterfaceMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    A monitored interface.
    """

    name = models.CharField(max_length=50)
    hw_address = registry_fields.MACAddressField()
    tx_packets = models.BigIntegerField()
    rx_packets = models.BigIntegerField()
    tx_bytes = models.BigIntegerField()
    rx_bytes = models.BigIntegerField()
    tx_errors = models.BigIntegerField()
    rx_errors = models.BigIntegerField()
    tx_drops = models.BigIntegerField()
    rx_drops = models.BigIntegerField()
    mtu = models.IntegerField()

    class RegistryMeta:
        registry_id = 'core.interfaces'
        multiple = True

registration.point('node.monitoring').register_item(InterfaceMonitor)


class WifiInterfaceMonitor(InterfaceMonitor):
    """
    A monitored wireless interface.
    """

    mode = registry_fields.SelectorKeyField('node.config', 'core.interfaces#wifi_mode')
    essid = models.CharField(max_length=50, null=True)
    bssid = registry_fields.MACAddressField(null=True)
    protocol = models.CharField(max_length=50)
    channel = models.PositiveIntegerField(null=True)
    channel_width = models.PositiveIntegerField(null=True)
    bitrate = models.FloatField(null=True)
    rts_threshold = models.IntegerField(null=True)
    frag_threshold = models.IntegerField(null=True)
    signal = models.IntegerField(null=True)
    noise = models.IntegerField(null=True)
    snr = models.FloatField()

    class RegistryMeta(InterfaceMonitor.RegistryMeta):
        pass

registration.point('node.monitoring').register_item(WifiInterfaceMonitor)

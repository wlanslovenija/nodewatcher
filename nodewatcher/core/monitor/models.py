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

    uptime = models.PositiveIntegerField(null=True)
    local_time = models.DateTimeField(null=True)

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        registry_id = 'system.status'

registration.point('node.monitoring').register_item(SystemStatusMonitor)


class GeneralResourcesMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    General resources such as load average, system memory and the number of processes.
    """

    loadavg_1min = models.FloatField(null=True)
    loadavg_5min = models.FloatField(null=True)
    loadavg_15min = models.FloatField(null=True)
    memory_free = models.PositiveIntegerField(null=True)
    memory_buffers = models.PositiveIntegerField(null=True)
    memory_cache = models.PositiveIntegerField(null=True)
    processes = models.PositiveIntegerField(null=True)

    class RegistryMeta:
        registry_id = 'system.resources.general'

registration.point('node.monitoring').register_item(GeneralResourcesMonitor)


class NetworkResourcesMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Network resources such as number of routes and number of tracked TCP and UDP
    connections.
    """

    routes = models.IntegerField(null=True)
    tcp_connections = models.IntegerField(null=True)
    udp_connections = models.IntegerField(null=True)

    class RegistryMeta:
        registry_id = 'system.resources.network'

registration.point('node.monitoring').register_item(NetworkResourcesMonitor)


class InterfaceMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    A monitored interface.
    """

    name = models.CharField(max_length=50, null=True)
    hw_address = registry_fields.MACAddressField(null=True)
    tx_packets = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    rx_packets = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    tx_bytes = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    rx_bytes = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    tx_errors = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    rx_errors = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    tx_drops = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    rx_drops = models.DecimalField(max_digits=100, decimal_places=0, null=True)
    mtu = models.IntegerField(null=True)

    class RegistryMeta:
        registry_id = 'core.interfaces'
        multiple = True

registration.point('node.monitoring').register_item(InterfaceMonitor)


class WifiInterfaceMonitor(InterfaceMonitor):
    """
    A monitored wireless interface.
    """

    mode = registry_fields.SelectorKeyField('node.config', 'core.interfaces#wifi_mode', null=True)
    essid = models.CharField(max_length=50, null=True)
    bssid = registry_fields.MACAddressField(null=True)
    protocol = models.CharField(max_length=50, null=True)
    channel = models.PositiveIntegerField(null=True)
    channel_width = models.PositiveIntegerField(null=True)
    bitrate = models.FloatField(null=True)
    rts_threshold = models.IntegerField(null=True)
    frag_threshold = models.IntegerField(null=True)
    signal = models.IntegerField(null=True)
    noise = models.IntegerField(null=True)
    snr = models.FloatField(null=True)

    class RegistryMeta(InterfaceMonitor.RegistryMeta):
        pass

registration.point('node.monitoring').register_item(WifiInterfaceMonitor)


class Measurement(models.Model):
    """
    Mixin for measurement monitor models.
    """

    source = models.ForeignKey(core_models.Node, null=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class RttMeasurementMonitor(registration.bases.NodeMonitoringRegistryItem, Measurement):
    """
    RTT measurements.
    """

    packet_size = models.PositiveIntegerField(null=True)
    packet_loss = models.PositiveIntegerField(null=True)
    all_packets = models.PositiveIntegerField(null=True)
    successful_packets = models.PositiveIntegerField(null=True)
    failed_packets = models.PositiveIntegerField(null=True)
    rtt_minimum = models.FloatField(null=True)
    rtt_average = models.FloatField(null=True)
    rtt_maximum = models.FloatField(null=True)

    class RegistryMeta:
        registry_id = 'network.measurement.rtt'
        multiple = True

registration.point('node.monitoring').register_item(RttMeasurementMonitor)

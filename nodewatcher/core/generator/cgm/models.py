import datetime
import random
import string

from django import dispatch
from django.core import exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _

from guardian import shortcuts
from timedelta import fields as timedelta_fields

from .. import models as generator_models
from ... import models as core_models
from ...allocation.ip import models as ip_models
from ...registry import fields as registry_fields, registration, permissions

from . import base as cgm_base

# Register a new firmware-generating permission
permissions.register(core_models.Node, 'generate_firmware', _("Can generate firmware"))

# In case we have the frontend module installed, we also subscribe to its
# node created signal that gets called when a node is created via the editor
try:
    from nodewatcher.modules.frontend.editor import signals as editor_signals

    @dispatch.receiver(editor_signals.post_create_node)
    def cgm_node_created(sender, request, node, **kwargs):
        """
        Assign generate_firmware permission to user that has created the node.
        """

        shortcuts.assign_perm('generate_firmware', request.user, node)
except ImportError:
    pass


class CgmGeneralConfig(core_models.GeneralConfig):
    """
    Extended general configuration that contains CGM-related options.
    """

    platform = registry_fields.RegistryChoiceField('node.config', 'core.general#platform', blank=True)
    router = registry_fields.RegistryChoiceField('node.config', 'core.general#router', blank=True)
    build_channel = registry_fields.ModelRegistryChoiceField(
        generator_models.BuildChannel,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    version = registry_fields.ModelRegistryChoiceField(
        generator_models.BuildVersion,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class RegistryMeta(core_models.GeneralConfig.RegistryMeta):
        registry_name = _("CGM Configuration")
        hides_parent = True

    def get_device(self):
        """
        Returns the device descriptor for the configured router.
        """

        return cgm_base.get_platform(self.platform).get_device(self.router)

registration.point('node.config').register_item(CgmGeneralConfig)


class AuthenticationConfig(registration.bases.NodeConfigRegistryItem):
    """
    Configuration for different authentication mechanisms.
    """

    class RegistryMeta:
        form_weight = 10
        registry_id = 'core.authentication'
        registry_section = _("Authentication")
        registry_name = _("Null Authentication")
        multiple = True
        hidden = True

registration.point("node.config").register_item(AuthenticationConfig)


class PasswordAuthenticationConfig(AuthenticationConfig):
    """
    Password authentication mechanism configuration.
    """

    password = models.CharField(max_length=30)

    class RegistryMeta(AuthenticationConfig.RegistryMeta):
        registry_name = _("Password")

registration.point('node.config').register_item(PasswordAuthenticationConfig)


# TODO: Should this go to OpenWrt module?
class PackageConfig(registration.bases.NodeConfigRegistryItem):
    """
    Common configuration for CGM packages.
    """

    enabled = models.BooleanField(default=True)

    class RegistryMeta:
        form_weight = 100
        registry_id = 'core.packages'
        registry_section = _("Extra Packages")
        registry_name = _("Package Configuration")
        multiple = True
        hidden = True

registration.point('node.config').register_item(PackageConfig)


class RoutableInterface(models.Model):
    class Meta:
        abstract = True

    routing_protocols = registry_fields.RegistryMultipleChoiceField(
        'node.config', 'core.interfaces#routing_protocol',
        blank=True, null=True, default=[],
    )


class InterfaceConfig(registration.bases.NodeConfigRegistryItem):
    """
    Interface configuration.
    """

    enabled = models.BooleanField(default=True)

    class RegistryMeta:
        form_weight = 50
        registry_id = 'core.interfaces'
        registry_section = _("Network Interface Configuration")
        registry_name = _("Generic Interface")
        multiple = True
        hidden = True

registration.point('node.config').register_item(InterfaceConfig)


class BridgeInterfaceConfig(InterfaceConfig, RoutableInterface):
    """
    Bridge interface configuration.
    """

    name = models.CharField(max_length=30)
    stp = models.BooleanField(verbose_name=_("STP"), default=False)
    mac_address = registry_fields.MACAddressField(verbose_name=_("Override MAC Address"), null=True, blank=True)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        registry_name = _("Bridge")

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        super(BridgeInterfaceConfig, self).__init__(*args, **kwargs)
        # Automatically generate a random bridge name when one does not exist
        if not self.name:
            self.name = "Bridge%(id)s" % {'id': random.choice(string.uppercase)}

    def __unicode__(self):
        if not self.name:
            return "(unnamed bridge)"

        return self.name

registration.point('node.config').register_item(BridgeInterfaceConfig)


class EthernetInterfaceConfig(InterfaceConfig, RoutableInterface):
    """
    An ethernet interface.
    """

    eth_port = registry_fields.RegistryChoiceField('node.config', 'core.interfaces#eth_port')
    uplink = models.BooleanField(default=False)
    mac_address = registry_fields.MACAddressField(verbose_name=_("Override MAC Address"), null=True, blank=True)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        registry_name = _("Ethernet Interface")

registration.point('node.config').register_item(EthernetInterfaceConfig)


class WifiRadioDeviceConfig(InterfaceConfig):
    """
    A wireless radio device.
    """

    wifi_radio = registry_fields.RegistryChoiceField('node.config', 'core.interfaces#wifi_radio')
    protocol = models.CharField(max_length=50)
    channel_width = models.CharField(max_length=50)
    channel = models.CharField(max_length=50, blank=True, null=True)
    antenna_connector = models.CharField(max_length=50, null=True)
    tx_power = models.PositiveSmallIntegerField(blank=True, null=True)
    ack_distance = models.IntegerField(null=True, blank=True, verbose_name=_("ACK Distance"))

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        registry_name = _("Wireless Radio")

registration.point('node.config').register_item(WifiRadioDeviceConfig)


class WifiInterfaceConfig(InterfaceConfig, RoutableInterface):
    """
    Wifi interface configuration.
    """

    device = registry_fields.IntraRegistryForeignKey(
        WifiRadioDeviceConfig, editable=False, null=False, related_name='interfaces'
    )

    mode = registry_fields.RegistryChoiceField('node.config', 'core.interfaces#wifi_mode')
    # For STA nodes, store (optional) where they are connected to.
    connect_to = models.ForeignKey(core_models.Node, blank=True, null=True, related_name='+')
    essid = models.CharField(max_length=50, null=True, verbose_name="ESSID")
    bssid = registry_fields.MACAddressField(verbose_name="BSSID", blank=True, null=True)
    uplink = models.BooleanField(default=False)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        form_weight = 51
        registry_section = _("Wireless Sub-Interfaces")
        registry_name = _("Wireless Interface")
        multiple = True
        hidden = False

    def get_target_interface(self):
        """
        Retrieve target (AP) node's interface configuration (for STA interfaces).
        """

        if self.connect_to is None:
            return

        try:
            target_node = self.connect_to
            # Retrieve the target wireless interface (the first AP interface for the same
            # protocol as this one).
            return target_node.config.core.interfaces(queryset=True).filter(
                WifiInterfaceConfig___mode='ap',
                WifiInterfaceConfig___device__protocol=self.device.protocol,
            )[0]
        except (core_models.Node.DoesNotExist, IndexError):
            return

    def get_index(self):
        """
        Returns the index of this interface among all of the node's VIFs of
        the same mode.
        """

        vifs = self.root.config.core.interfaces(
            onlyclass=WifiInterfaceConfig,
        ).filter(
            WifiInterfaceConfig___mode=self.mode,
        ).order_by('pk').values_list('pk', flat=True)

        return list(vifs).index(self.pk)

registration.point('node.config').register_choice('core.interfaces#wifi_mode', registration.Choice('mesh', _("Mesh")))
registration.point('node.config').register_choice('core.interfaces#wifi_mode', registration.Choice('ap', _("AP")))
registration.point('node.config').register_choice('core.interfaces#wifi_mode', registration.Choice('sta', _("STA")))
registration.point('node.config').register_subitem(WifiRadioDeviceConfig, WifiInterfaceConfig)


class MobileInterfaceConfig(InterfaceConfig):
    """
    A mobile (3G/UMTS/GPRS) interface.
    """

    service = registry_fields.RegistryChoiceField('node.config', 'core.interfaces#mobile_service', default='umts')
    device = registry_fields.RegistryChoiceField('node.config', 'core.interfaces#mobile_device', default='ppp0')
    apn = models.CharField(max_length=100, verbose_name=_("APN"))
    pin = models.CharField(max_length=4, blank=True, verbose_name=_("PIN"))
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    uplink = models.BooleanField(default=False)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        registry_name = _("Mobile Interface")

registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('ppp0', _("PPP over USB0")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('qmi0', _("QMI over USB0")))
registration.point('node.config').register_choice('core.interfaces#mobile_service', registration.Choice('umts', _("UMTS")))
registration.point('node.config').register_choice('core.interfaces#mobile_service', registration.Choice('gprs', _("GPRS")))
registration.point('node.config').register_choice('core.interfaces#mobile_service', registration.Choice('cdma', _("CDMA")))
registration.point('node.config').register_item(MobileInterfaceConfig)


class AnnouncableNetwork(models.Model):
    class Meta:
        abstract = True

    routing_announces = registry_fields.RegistryMultipleChoiceField(
        'node.config', 'core.interfaces.network#routing_announce',
        blank=True, null=True, verbose_name=_("Announce Via"), default=[],
    )


class LeasableNetwork(models.Model):
    """
    Abstract class for networks which may be leased to clients via DHCP.
    """

    lease_type = registry_fields.RegistryChoiceField(
        'node.config', 'core.interfaces.network#lease_type',
        blank=True, null=True, verbose_name=_("Lease Type"),
    )
    lease_duration = timedelta_fields.TimedeltaField(
        default='15min',
        verbose_name=_("Lease Duration"),
        choices=(
            (datetime.timedelta(minutes=15), _("15 minutes")),
            (datetime.timedelta(minutes=30), _("30 minutes")),
            (datetime.timedelta(hours=1), _("1 hour")),
            (datetime.timedelta(hours=2), _("2 hours")),
            (datetime.timedelta(hours=4), _("4 hours")),
            (datetime.timedelta(hours=12), _("12 hours")),
            (datetime.timedelta(hours=24), _("24 hours")),
        )
    )
    nat_type = registry_fields.RegistryChoiceField(
        'node.config', 'core.interfaces.network#nat_type',
        blank=True, null=True, verbose_name=_("NAT Type"),
    )

    class Meta:
        abstract = True

registration.point('node.config').register_choice('core.interfaces.network#lease_type', registration.Choice('dhcp', _("DHCP")))
registration.point('node.config').register_choice('core.interfaces.network#nat_type', registration.Choice('snat-routed-networks', _("SNAT (towards routed networks)")))
# TODO: Support other kinds of SNAT, for example over the uplink interface(s).


class NetworkConfig(registration.bases.NodeConfigRegistryItem):
    """
    Network configuration of an interface.
    """

    interface = registry_fields.IntraRegistryForeignKey(InterfaceConfig, editable=False, null=False, related_name='networks')
    enabled = models.BooleanField(default=True)
    description = models.CharField(max_length=100, blank=True)

    class RegistryMeta:
        form_weight = 51
        registry_id = 'core.interfaces.network'
        registry_section = _("Network Configuration")
        registry_name = _("Generic Network Config")
        multiple = True
        hidden = True

registration.point('node.config').register_subitem(InterfaceConfig, NetworkConfig)


class BridgedNetworkConfig(NetworkConfig):
    """
    Network configuration that puts the interface into a bridge.
    """

    bridge = registry_fields.ReferenceChoiceField(BridgeInterfaceConfig, related_name='bridge_ports')

    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("Bridged")

registration.point('node.config').register_subitem(EthernetInterfaceConfig, BridgedNetworkConfig)
registration.point('node.config').register_subitem(WifiInterfaceConfig, BridgedNetworkConfig)


class StaticNetworkConfig(NetworkConfig, AnnouncableNetwork, LeasableNetwork):
    """
    Static IP configuration.
    """

    family = registry_fields.RegistryChoiceField('node.config', 'core.interfaces.network#ip_family')
    address = registry_fields.IPAddressField(subnet_required=True)
    gateway = registry_fields.IPAddressField(host_required=True, null=True, blank=True)

    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("Static Network")

    def clean(self):
        """
        Verifies that gateway is in the address subnet.
        """

        if not self.address or not self.gateway:
            return

        family = 6 if self.family == 'ipv6' else 4
        if not (self.address.version == self.gateway.version == family):
            raise exceptions.ValidationError(_("You must specify IP addresses of the selected address family!"))

        if self.gateway not in self.address:
            raise exceptions.ValidationError(_("Specified gateway is not part of the host's subnet!"))

        if self.gateway.ip == self.address.ip:
            raise exceptions.ValidationError(_("Host address and gateway address must be different!"))

registration.point('node.config').register_choice('core.interfaces.network#ip_family', registration.Choice('ipv4', _("IPv4")))
registration.point('node.config').register_choice('core.interfaces.network#ip_family', registration.Choice('ipv6', _("IPv6")))
registration.point('node.config').register_subitem(EthernetInterfaceConfig, StaticNetworkConfig)
registration.point('node.config').register_subitem(WifiInterfaceConfig, StaticNetworkConfig)
registration.point('node.config').register_subitem(BridgeInterfaceConfig, StaticNetworkConfig)


class DHCPNetworkConfig(NetworkConfig):
    """
    DHCP IP configuration.
    """

    # No additional fields
    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("DHCP")

registration.point('node.config').register_subitem(EthernetInterfaceConfig, DHCPNetworkConfig)
registration.point('node.config').register_subitem(WifiInterfaceConfig, DHCPNetworkConfig)
registration.point('node.config').register_subitem(BridgeInterfaceConfig, DHCPNetworkConfig)


class AllocatedNetworkConfig(NetworkConfig, ip_models.IpAddressAllocator, AnnouncableNetwork, LeasableNetwork):
    """
    IP configuration that gets allocated from a pool.
    """

    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("Allocated Network")

registration.point('node.config').register_subitem(EthernetInterfaceConfig, AllocatedNetworkConfig)
registration.point('node.config').register_subitem(WifiInterfaceConfig, AllocatedNetworkConfig)
registration.point('node.config').register_subitem(BridgeInterfaceConfig, AllocatedNetworkConfig)


class PPPoENetworkConfig(NetworkConfig):
    """
    Configuration for a WAN PPPoE uplink.
    """

    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("PPPoE")

registration.point('node.config').register_subitem(EthernetInterfaceConfig, PPPoENetworkConfig)


class InterfaceLimitConfig(registration.bases.NodeConfigRegistryItem):
    """
    Configuration of per-interface traffic limits.
    """

    interface = registry_fields.IntraRegistryForeignKey(InterfaceConfig, editable=False, null=False, related_name='limits')
    enabled = models.BooleanField(default=True)

    class RegistryMeta:
        form_weight = 50
        registry_id = 'core.interfaces.limits'
        registry_section = _("Traffic Limits Configuration")
        registry_name = _("Generic Limits")
        multiple = True
        hidden = True

registration.point('node.config').register_subitem(InterfaceConfig, InterfaceLimitConfig)


class ThroughputInterfaceLimitConfig(InterfaceLimitConfig):
    """
    Throughput limit configuration.
    """

    limit_out = registry_fields.RegistryChoiceField(
        'node.config', 'core.interfaces.limits#speeds',
        verbose_name=_("Upload limit"), default='', blank=True,
    )
    limit_in = registry_fields.RegistryChoiceField(
        'node.config', 'core.interfaces.limits#speeds',
        verbose_name=_("Download limit"), default='', blank=True,
    )

    class RegistryMeta(InterfaceLimitConfig.RegistryMeta):
        registry_name = _("Throughput Limit")
        hidden = False

# TODO: This probably shouldn't be hardcoded, it should be moved to modules.administration?
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('128', _("128 Kbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('256', _("256 Kbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('512', _("512 Kbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('1024', _("1 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('2048', _("2 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('4096', _("4 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('6144', _("6 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('8192', _("8 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('10240', _("10 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('15360', _("15 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('20480', _("20 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('25600', _("25 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('30720', _("30 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('40960', _("40 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('51200', _("50 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('61440', _("60 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('71680', _("70 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('81920', _("80 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('92160', _("90 Mbit/s")))
registration.point('node.config').register_choice('core.interfaces.limits#speeds', registration.Choice('102400', _("100 Mbit/s")))

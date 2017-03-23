import datetime
import random
import string

from django import dispatch
from django.core import exceptions
from django.contrib.postgres import fields as postgres_fields
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

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

        if not self.router:
            return None

        try:
            return cgm_base.get_platform(self.platform).get_device(self.router)
        except KeyError:
            return None

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
        sensitive_fields = ['password']

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


class SwitchConfig(registration.bases.NodeConfigRegistryItem):
    """
    Switch configuration.
    """

    switch = registry_fields.RegistryChoiceField('node.config', 'core.switch#switch')
    # Valid VLAN presets are defined by the device descriptor based for a specific switch.
    vlan_preset = models.CharField(max_length=50)

    class RegistryMeta:
        form_weight = 40
        registry_id = 'core.switch'
        registry_section = _("Switch")
        registry_name = _("Switch Configuration")
        multiple = True

registration.point('node.config').register_item(SwitchConfig)


class VLANConfig(registration.bases.NodeConfigRegistryItem):
    """
    VLAN configuration for a specific switch.
    """

    switch = registry_fields.IntraRegistryForeignKey(SwitchConfig, editable=False, null=False, related_name='vlans')
    name = models.CharField(max_length=30)
    # Valid VLANs are defined by the device descriptor for a specific switch.
    vlan = models.IntegerField()
    # Valid ports are defined by the device descriptor for a specific switch.
    ports = postgres_fields.ArrayField(models.IntegerField(), default=list)

    class RegistryMeta:
        registry_id = 'core.switch.vlan'
        registry_section = _("VLAN")
        registry_name = _("VLAN Configuration")
        multiple = True

    def __unicode__(self):
        if not self.name:
            return ugettext("VLAN %(switch)s.vlan%(vlan)s") % {'switch': self.switch.switch, 'vlan': self.vlan}

        return ugettext("VLAN %(switch)s.vlan%(vlan)s (%(name)s)") % {
            'switch': self.switch.switch,
            'vlan': self.vlan,
            'name': self.name
        }

registration.point('node.config').register_subitem(SwitchConfig, VLANConfig)


class RoutableInterface(models.Model):
    class Meta:
        abstract = True

    routing_protocols = registry_fields.RegistryMultipleChoiceField(
        'node.config', 'core.interfaces#routing_protocol',
        blank=True, null=True, default=list,
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

    def has_child_interfaces(self):
        """
        Interface implementations may return True if this interface can have
        any child interfaces.
        """

        return False

    def get_child_interfaces(self):
        """
        Interface implementations may return a queryset that accesses any child
        interfaces.
        """

        return InterfaceConfig.objects.none()

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
            return ugettext("Bridge interface (unnamed)")

        return ugettext("Bridge interface (%(name)s)") % {'name': self.name}

registration.point('node.config').register_item(BridgeInterfaceConfig)


class EthernetInterfaceConfig(InterfaceConfig, RoutableInterface):
    """
    An ethernet interface.
    """

    eth_port = models.CharField(max_length=50)
    uplink = models.BooleanField(default=False)
    mac_address = registry_fields.MACAddressField(verbose_name=_("Override MAC Address"), null=True, blank=True)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        registry_name = _("Ethernet Interface")

    def __unicode__(self):
        if not self.eth_port:
            return ugettext("Ethernet interface (unbound)")

        return ugettext("Ethernet interface (%(eth_port)s)") % {'eth_port': self.eth_port}

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

    def has_child_interfaces(self):
        return True

    def get_child_interfaces(self):
        return self.interfaces.all()

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
    bitrates_preset = registry_fields.RegistryChoiceField(
        'node.config',
        'core.interfaces#wifi_bitrates_preset',
        null=True,
        blank=True,
    )
    bitrates = postgres_fields.ArrayField(
        models.CharField(max_length=50),
        blank=True,
        null=True,
        default=list,
    )
    isolate_clients = models.BooleanField(
        default=True,
        help_text=_("Enable to isolate clients connected to the same AP from each other."),
    )
    uplink = models.BooleanField(default=False)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        form_weight = 51
        registry_section = _("Wireless Sub-Interfaces")
        registry_name = _("Wireless Interface")
        multiple = True
        hidden = False

    def save(self, **kwargs):
        """
        Save handler.
        """

        # The value of isolate_clients cannot be null, but the field is removed from the
        # form for non-AP configurations, which would cause the field to be NULL.
        if not self.isolate_clients:
            self.isolate_clients = False

        super(WifiInterfaceConfig, self).save(**kwargs)

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
registration.point('node.config').register_choice('core.interfaces#wifi_bitrates_preset', registration.Choice(None, _("Allow all supported bitrates")))
registration.point('node.config').register_choice('core.interfaces#wifi_bitrates_preset', registration.Choice('exclude-80211b', _("Exclude legacy 802.11b bitrates")))
registration.point('node.config').register_choice('core.interfaces#wifi_bitrates_preset', registration.Choice('exclude-80211bg', _("Exclude legacy 802.11b/g bitrates")))
registration.point('node.config').register_choice('core.interfaces#wifi_bitrates_preset', registration.Choice('custom', _("Custom bitrate configuration")))
registration.point('node.config').register_subitem(WifiRadioDeviceConfig, WifiInterfaceConfig)


class MobileInterfaceConfig(InterfaceConfig):
    """
    A mobile (3G/UMTS/GPRS) interface.
    """

    device = registry_fields.RegistryChoiceField('node.config', 'core.interfaces#mobile_device', default='ppp0')
    service = registry_fields.RegistryChoiceField('node.config', 'core.interfaces#mobile_service', default='umts')
    apn = models.CharField(max_length=100, verbose_name=_("APN"))
    pin = models.CharField(max_length=4, blank=True, verbose_name=_("PIN"))
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    uplink = models.BooleanField(default=False)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        registry_name = _("Mobile Interface")
        sensitive_fields = ['pin', 'username', 'password']

    def __unicode__(self):
        if not self.device:
            return ugettext("Mobile interface (unbound)")

        return ugettext("Mobile interface (%(device)s)") % {'device': self.get_device_display()}

registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('ppp0', _("PPP over USB0")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('ppp1', _("PPP over USB1")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('ppp2', _("PPP over USB2")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('ppp3', _("PPP over USB3")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('qmi0', _("QMI over USB0")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('qmi1', _("QMI over USB1")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('qmi2', _("QMI over USB2")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('eth-cdc0', _("Ethernet over CDC-USB0")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('eth-cdc1', _("Ethernet over CDC-USB1")))
registration.point('node.config').register_choice('core.interfaces#mobile_device', registration.Choice('eth-cdc2', _("Ethernet over CDC-USB2")))
registration.point('node.config').register_choice('core.interfaces#mobile_service', registration.Choice('umts', _("UMTS")))
registration.point('node.config').register_choice('core.interfaces#mobile_service', registration.Choice('gprs', _("GPRS")))
registration.point('node.config').register_choice('core.interfaces#mobile_service', registration.Choice('cdma', _("CDMA")))
registration.point('node.config').register_item(MobileInterfaceConfig)


class AnnouncableNetwork(models.Model):
    class Meta:
        abstract = True

    routing_announces = registry_fields.RegistryMultipleChoiceField(
        'node.config', 'core.interfaces.network#routing_announce',
        blank=True, null=True, verbose_name=_("Announce Via"), default=list,
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

    dns = models.BooleanField(default=False, verbose_name=_("Use received DNS server"))
    default_route = models.BooleanField(default=True, verbose_name=_("Create default route via received gateway"))

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

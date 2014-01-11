from django.conf import settings
from django.core import exceptions
from django.db import models
from django.utils.translation import ugettext as _

from ... import models as core_models
from ...allocation.ip import models as ip_models
from ...registry import fields as registry_fields, registration, permissions

from . import base as cgm_base

# Register a new firmware-generating permission
permissions.register(core_models.Node, 'can_generate_firmware', _("Can generate firmware"))


class CgmGeneralConfig(core_models.GeneralConfig):
    """
    Extended general configuration that contains CGM-related options.
    """

    platform = registry_fields.SelectorKeyField('node.config', 'core.general#platform', blank=True)
    router = registry_fields.SelectorKeyField('node.config', 'core.general#router', blank=True)
    version = registry_fields.SelectorKeyField('node.config', 'core.general#version', blank=True)

    class RegistryMeta(core_models.GeneralConfig.RegistryMeta):
        registry_name = _("CGM Configuration")
        hides_parent = True

    def get_device(self):
        """
        Returns the device descriptor for the configured router.
        """

        return cgm_base.get_platform(self.platform).get_device(self.router)

# Register all configured versions
for platform, cfg in settings.GENERATOR_BUILDERS.items():
    for version, (builder, name) in cfg['versions'].items():
        registration.point('node.config').register_choice(
            'core.general#version',
            registration.Choice(
                version,
                name,
                limited_to=('core.general#platform', platform),
            )
        )

registration.point('node.config').register_item(CgmGeneralConfig)


class AuthenticationConfig(registration.bases.NodeConfigRegistryItem):
    """
    Configuration for different authentication mechanisms.
    """

    class RegistryMeta:
        form_weight = 10
        registry_id = 'core.authentication'
        registry_section = _("Authentication")
        registry_name = _("Basic Authentication")
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

    routing_protocol = registry_fields.SelectorKeyField(
        'node.config', 'core.interfaces#routing_protocol',
        blank=True, null=True,
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


class EthernetInterfaceConfig(InterfaceConfig, RoutableInterface):
    """
    An ethernet interface.
    """

    eth_port = registry_fields.SelectorKeyField('node.config', 'core.interfaces#eth_port')
    uplink = models.BooleanField(default=False)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        registry_name = _("Ethernet Interface")

registration.point('node.config').register_item(EthernetInterfaceConfig)


class WifiRadioDeviceConfig(InterfaceConfig):
    """
    A wireless radio device.
    """

    wifi_radio = registry_fields.SelectorKeyField('node.config', 'core.interfaces#wifi_radio')
    protocol = models.CharField(max_length=50)
    channel_width = models.CharField(max_length=50)
    channel = models.CharField(max_length=50)
    bitrate = models.IntegerField(default=11)
    antenna_connector = models.CharField(max_length=50, null=True)
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

    mode = registry_fields.SelectorKeyField('node.config', 'core.interfaces#wifi_mode')
    essid = models.CharField(max_length=50, verbose_name="ESSID")
    bssid = registry_fields.MACAddressField(verbose_name="BSSID")

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        form_weight = 51
        registry_name = _("Wireless Interface")
        multiple = True
        hidden = False

registration.point('node.config').register_choice('core.interfaces#wifi_mode', registration.Choice('mesh', _("Mesh")))
registration.point('node.config').register_choice('core.interfaces#wifi_mode', registration.Choice('ap', _("AP")))
registration.point('node.config').register_choice('core.interfaces#wifi_mode', registration.Choice('sta', _("STA")))
registration.point('node.config').register_subitem(WifiRadioDeviceConfig, WifiInterfaceConfig)


# TODO: Is it important if it is tap or tun? Should we have separate configs for them? Or is this more general? Maybe better name then VirtualInterface, PseudoWire, or something?
class VpnInterfaceConfig(InterfaceConfig, RoutableInterface):
    """
    VPN interface.
    """

    protocol = registry_fields.SelectorKeyField('node.config', 'core.interfaces#vpn_protocol', verbose_name=_("VPN Protocol"))
    mac = registry_fields.MACAddressField(auto_add=True)

    class RegistryMeta(InterfaceConfig.RegistryMeta):
        registry_name = _("VPN Tunnel")

registration.point('node.config').register_item(VpnInterfaceConfig)


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

registration.point('node.config').register_subitem(InterfaceConfig, NetworkConfig)


class StaticNetworkConfig(NetworkConfig):
    """
    Static IP configuration.
    """

    family = registry_fields.SelectorKeyField('node.config', 'core.interfaces.network#ip_family')
    address = registry_fields.IPAddressField(subnet_required=True)
    gateway = registry_fields.IPAddressField(host_required=True)

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


class DHCPNetworkConfig(NetworkConfig):
    """
    DHCP IP configuration.
    """

    # No additional fields
    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("DHCP")

registration.point('node.config').register_subitem(EthernetInterfaceConfig, DHCPNetworkConfig)


class AllocatedNetworkConfig(NetworkConfig, ip_models.IpAddressAllocator):
    """
    IP configuration that gets allocated from a pool.
    """

    routing_announce = registry_fields.SelectorKeyField(
        'node.config', 'core.interfaces.network#routing_announce',
        blank=True, null=True, verbose_name=_("Announce Via"),
    )

    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("Allocated Network")

registration.point('node.config').register_subitem(EthernetInterfaceConfig, AllocatedNetworkConfig)
registration.point('node.config').register_subitem(WifiInterfaceConfig, AllocatedNetworkConfig)


class PPPoENetworkConfig(NetworkConfig):
    """
    Configuration for a WAN PPPoE uplink.
    """

    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("PPPoE")

registration.point('node.config').register_subitem(EthernetInterfaceConfig, PPPoENetworkConfig)


class VpnNetworkConfig(NetworkConfig):
    """
    Configuration for a VPN uplink.
    """

    address = registry_fields.IPAddressField(host_required=True)
    port = models.IntegerField()

    class RegistryMeta(NetworkConfig.RegistryMeta):
        registry_name = _("VPN Server")

registration.point('node.config').register_subitem(VpnInterfaceConfig, VpnNetworkConfig)


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

    limit_out = registry_fields.SelectorKeyField(
        'node.config', 'core.interfaces.limits#speeds',
        verbose_name=_("Limit OUT"), default='', blank=True,
    )
    limit_in = registry_fields.SelectorKeyField(
        'node.config', 'core.interfaces.limits#speeds',
        verbose_name=_("Limit IN"), default='', blank=True,
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
registration.point('node.config').register_subitem(VpnInterfaceConfig, ThroughputInterfaceLimitConfig)

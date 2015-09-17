from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base, models as cgm_models

from . import models


@cgm_base.register_platform_module('openwrt', 500)
def commotion_network(node, cfg):
    """
    Configures commotion network on OpenWrt.
    """

    device = node.config.core.general().get_device()

    for network in node.config.core.interfaces.network(onlyclass=models.CommotionNetworkConfig):
        interface = network.interface

        if isinstance(interface, cgm_models.EthernetInterfaceConfig):
            name = interface.eth_port
        elif isinstance(interface, cgm_models.WifiInterfaceConfig):
            name = device.get_vif_mapping('openwrt', interface.wifi_radio, interface)
        elif isinstance(interface, cgm_models.BridgeInterfaceConfig):
            name = device.get_bridge_mapping('openwrt', interface)
        else:
            raise cgm_base.ValidationError(
                _("Unsupported interface type '%s' for OpenWrt commotion network configuration!") % interface.__class__.__name__
            )

        # The interface has been previously configured by the base platform CGM.
        iface = cfg.network.find_named_section('interface', _key=name)
        iface.proto = 'commotion'

        # Class.
        if network.network_class == 'mesh':
            iface['class'] = 'mesh'
        elif network.network_class == 'client':
            iface['class'] = 'client'
        elif network.network_class == 'wired':
            iface['class'] = 'wired'
        else:
            raise cgm_base.ValidationError(
                _("Unsupported network class '%s' for OpenWrt commotion network configuration!") % network.network_class
            )

        # DHCP.
        if network.dhcp:
            if network.dhcp == 'auto':
                iface.dhcp = 'auto'
            elif network.dhcp == 'server':
                iface.dhcp = 'server'
            elif network.dhcp == 'client':
                iface.dhcp = 'client'
            else:
                raise cgm_base.ValidationError(
                    _("Unsupported DHCP option '%s' for OpenWrt commotion network configuration!") % network.dhcp
                )

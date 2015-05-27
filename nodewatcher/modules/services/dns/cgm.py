from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def dns_servers(node, cfg):
    """
    Configures DNS servers.
    """

    # DNS configuration is part of the DHCP config.
    dnsmasq = cfg.dhcp.find_ordered_section('dnsmasq')
    dnsmasq.server = [str(x.server.address.ip) for x in node.config.core.servers.dns()]

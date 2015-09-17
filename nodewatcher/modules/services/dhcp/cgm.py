from nodewatcher.core.generator.cgm import base as cgm_base


@cgm_base.register_platform_module('openwrt', 900)
def dhcp_leases(node, cfg):
    """
    Configures DHCP leases.
    """

    for lease in node.config.core.dhcp.leases():
        host = cfg.dhcp.add('host')
        host.ip = str(lease.ip_address.ip)
        host.mac = lease.mac_address
        if lease.hostname:
            host.name = lease.hostname

from django.utils.translation import ugettext as _

from nodewatcher.core.registry import registration
from nodewatcher.core.generator.cgm import models as cgm_models, base as cgm_base

from . import models

# Register tunneldigger VPN protocol
registration.point('node.config').register_choice('core.interfaces#vpn_protocol', registration.Choice('tunneldigger', _("Tunneldigger")))


@cgm_base.register_platform_module('openwrt', 100)
def tunneldigger(node, cfg):
    """
    Configures the tunneldigger VPN solution.
    """

    # Deactivate tunneldigger when no uplink interface has been configured
    uplink_interface = None
    for name, section in cfg.network:
        if section.get_type() == 'interface' and section._uplink:
            uplink_interface = name
            break
    else:
        return

    # Create tunneldigger configuration
    tunneldigger_enabled = False
    for idx, interface in enumerate(node.config.core.interfaces(onlyclass=cgm_models.VpnInterfaceConfig)):
        if interface.protocol != 'tunneldigger':
            continue

        ifname = models.get_tunneldigger_interface_name(idx)
        tunneldigger_enabled = True

        # Create interface configurations; note that addressing configuration is routing
        # daemon dependent and as such should not be filled in here
        iface = cfg.network.add(interface=ifname)
        iface.ifname = ifname
        iface.macaddr = interface.mac
        iface.proto = 'none'
        iface._routable = interface.routing_protocol

        # Add a broker for each configured interface
        broker = cfg.tunneldigger.add('broker')
        broker.address = []
        unique_brokers = set()

        for network in interface.networks.filter(enabled=True):
            network = network.cast()
            broker.address.append('%s:%d' % (network.address.ip, network.port))
            unique_brokers.add(network.address)

        broker.uuid = node.uuid
        broker.interface = ifname

        # Configure downstream limits if any are defined for this interface
        for limit in interface.limits.filter(enabled=True):
            limit = limit.cast()
            if not isinstance(limit, cgm_models.ThroughputInterfaceLimitConfig):
                # We currently only support bandwidth limits, others are ignored as
                # far as tunneldigger is concerned
                continue

            if limit.limit_out:
                # Configure upload limit via local QoS
                qos = cfg.qos.add(interface=ifname)
                qos.enabled = True
                qos.classgroup = 'Default'
                qos.upload = limit.limit_out

            if limit.limit_in:
                broker.limit_bw_down = limit.limit_in
                # Only take the first bandwidth limit into account and ignore the rest
                break

        # Create routing policy entries to ensure tunneldigger connections are not
        # routed via the mesh
        for broker in unique_brokers:
            policy = cfg.routing.add('policy')
            policy.dest_ip = broker.ip
            policy.table = 'main'
            policy.priority = 500

            # Support policy routing configuration in trunk
            policy = cfg.network.add('rule')
            policy.dest = broker.ip
            policy.lookup = 'main'
            policy.priority = 500

    if tunneldigger_enabled:
        # Ensure that WAN traffic is routed via the main table
        policy = cfg.routing.add('policy')
        policy.device = uplink_interface
        policy.table = 'main'
        policy.priority = 500

        # Support policy routing configuration in trunk
        policy = cfg.network.add('rule')
        setattr(policy, 'in', uplink_interface)
        policy.lookup = 'main'
        policy.priority = 500

        # Register the 'tunneldigger' and 'policy-routing' packages
        cfg.packages.update(['tunneldigger', 'policy-routing'])

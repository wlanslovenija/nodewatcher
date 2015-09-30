from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import models as cgm_models, base as cgm_base

from . import models


@cgm_base.register_platform_module('openwrt', 100)
def tunneldigger(node, cfg):
    """
    Configures the tunneldigger VPN solution.
    """

    # Create tunneldigger configuration
    tunneldigger_enabled = False
    tunneldigger_ifaces = []
    for idx, interface in enumerate(node.config.core.interfaces(onlyclass=models.TunneldiggerInterfaceConfig)):
        ifname = models.get_tunneldigger_interface_name(idx)
        tunneldigger_enabled = True
        tunneldigger_ifaces.append(ifname)

        # Create interface configurations; note that addressing configuration is routing
        # daemon dependent and as such should not be filled in here
        iface = cfg.network.add(interface=ifname)
        iface.ifname = ifname
        iface.macaddr = interface.mac
        iface.proto = 'none'
        iface._routable = interface.routing_protocols

        # Add a broker for each configured interface
        broker = cfg.tunneldigger.add('broker')
        broker.address = []
        unique_brokers = set()

        for port in interface.server.ports:
            broker.address.append('%s:%d' % (interface.server.address.ip, port))
            unique_brokers.add(interface.server.address)

        broker.uuid = node.uuid
        broker.interface = ifname

        # Bind to specific interface when configured.
        if interface.uplink_interface:
            section = cfg.network.find_named_section('interface', _managed_by=interface.uplink_interface)
            if not section:
                raise cgm_base.ValidationError(_("Configured Tunneldigger uplink interface not found."))

            broker.bind_interface = section.get_key()

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

            # Only take the first bandwidth limit into account and ignore the rest.
            break

        # Create routing policy entries to ensure tunneldigger connections are not
        # routed via the mesh
        for broker in unique_brokers:
            policy = cfg.network.add('rule')
            policy.dest = "%s/32" % broker.ip
            policy.lookup = 'main'
            policy.priority = 500

    if tunneldigger_enabled:
        # Raise validation error when no uplink interface has been configured.
        uplink_interface = cfg.network.find_named_section('interface', _uplink=True)
        if not uplink_interface:
            raise cgm_base.ValidationError(_("In order to use Tunneldigger interfaces, an uplink interface must be defined!"))

        # Setup firewall policy for tunneldigger traffic
        firewall = cfg.firewall.add('zone')
        firewall.name = 'tunneldigger'
        firewall.network = tunneldigger_ifaces
        firewall.input = 'ACCEPT'
        firewall.output = 'ACCEPT'
        firewall.forward = 'ACCEPT'
        firewall.mtu_fix = True

        # Ensure that "tunneldigger" package is installed
        cfg.packages.update(['tunneldigger'])

from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base

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
        iface = cfg.network.add(interface=ifname, managed_by=interface)
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

        # Configure downstream limits if any are defined for this interface.
        try:
            for qos in interface.qos.filter(enabled=True):
                if qos.download:
                    broker.limit_bw_down = qos.download

                # Only take the first bandwidth limit into account and ignore the rest.
                break
        except AttributeError:
            # Support for QoS is not installed, skip any bandwidth limit configuration.
            pass

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


@cgm_base.register_platform_package('openwrt', 'tunneldigger-broker', models.TunneldiggerBrokerConfig)
def tunneldigger_broker(node, pkgcfg, cfg):
    """
    Configures a tunneldigger broker.
    """

    try:
        pkgcfg = pkgcfg.get()
    except models.TunneldiggerBrokerConfig.MultipleObjectsReturned:
        raise cgm_base.ValidationError(_("Only one tunneldigger broker may be defined."))

    # Configure the broker.
    broker = cfg['tunneldigger-broker'].add('broker')
    broker.port = pkgcfg.ports

    # Configure uplink interface.
    if not pkgcfg.uplink_interface:
        raise cgm_base.ValidationError(_("Tunneldigger broker must have an uplink interface configured."))

    section = cfg.network.find_named_section('interface', _managed_by=pkgcfg.uplink_interface)
    if not section:
        raise cgm_base.ValidationError(_("Configured tunneldigger broker uplink interface not found."))

    broker.interface = section.get_key()
    broker.max_cookies = pkgcfg.max_cookies
    broker.max_tunnels = pkgcfg.max_tunnels
    broker.port_base = 20000
    broker.tunnel_id_base = 100
    broker.tunnel_timeout = int(pkgcfg.tunnel_timeout.total_seconds())
    broker.pmtu_discovery = pkgcfg.pmtu_discovery
    broker.namespace = 'broker0'

    log = cfg['tunneldigger-broker'].add('log')
    log.filename = '/dev/null'
    log.verbosity = 'INFO'
    log.log_ip_addresses = False

    # Create routable digger interfaces.
    interfaces = []
    for mtu in (1280, 1346, 1396, 1422, 1438, 1446):
        ifname = models.get_tunneldigger_broker_interface_name(mtu)
        iface = cfg.network.add(interface=ifname, managed_by=pkgcfg)
        iface.ifname = ifname
        iface.type = 'bridge'
        iface.bridge_empty = True
        iface.proto = 'none'
        iface._routable = pkgcfg.routing_protocols

        bridge = cfg['tunneldigger-broker'].add('bridge')
        bridge.mtu = mtu
        bridge.interface = ifname

        interfaces.append(ifname)

    # Enable bridge iptables.
    cfg.sysctl.set_variable('net.bridge.bridge-nf-call-iptables', 1)
    cfg.packages.add('ebtables')

    # Configure firewall policy to prevent forwarding within the bridge.
    include = cfg.firewall.add('include')
    include.path = '/etc/firewall.tunneldigger'

    cfg.files.install(
        include.path,
        'tunneldigger/firewall',
        context={
            'interfaces': interfaces,
        }
    )

    # Ensure connection tracking is enabled on the uplink zone.
    firewall = cfg.firewall.find_ordered_section('zone', name='uplink')
    firewall.conntrack = True

    # Ensure all configured ports are allowed.
    rule = cfg.firewall.add('rule')
    rule.src = 'uplink'
    rule.proto = 'udp'
    rule.dest_port = pkgcfg.ports
    rule.target = 'ACCEPT'

from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base, resources as cgm_resources, models as cgm_models
from nodewatcher.utils import ipaddr

from . import models as babel_models, signals

ROUTING_TABLE_ID = 21
ROUTING_TABLE_NAME = 'babel'
ROUTING_TABLE_PRIORITY = 999
ROUTING_TABLE_DEFAULT_ID = 31
ROUTING_TABLE_DEFAULT_NAME = 'babel_default'
ROUTING_TABLE_DEFAULT_PRIORITY = 1099


class BabelProtocolManager(object):
    routing_protocol = babel_models.BABEL_PROTOCOL_NAME


def has_routing_protocol(manager, attribute):
    """
    Helper for determining whether a given manager has this routing
    protocol in a specific attribute. The value of this attribute
    may either be None or a list of protocol identifiers.
    """

    protocols = getattr(manager, attribute, None)
    if not protocols:
        return False

    return babel_models.BABEL_PROTOCOL_NAME in protocols


@cgm_base.register_platform_module('openwrt', 900)
def babel(node, cfg):
    babel_configured = False

    # Iterate through interfaces and decide which ones should be included in the routing table, based
    # on the presence of BABEL_PROTOCOL_NAME in the interface manager's "routing_protocols".
    routable_ifaces = []
    announced_ifaces = []
    announced_uplink_ifaces = []
    announced_networks = []
    for name, iface in list(cfg.network):
        if iface.get_type() != 'interface':
            continue

        manager = iface.get_manager()
        network_manager = iface.get_manager(cgm_models.NetworkConfig)

        # All interfaces that are marked for this routing protocol should be redistributed.
        if has_routing_protocol(network_manager, 'routing_announces'):
            net = ipaddr.IPNetwork('%s/%s' % (iface.ipaddr, iface.netmask))
            announced_networks.append(net)

            # For each announced interface add a static route to the Babel routing table.
            hna_route = cfg.network.add(route='babel_rt_%s' % iface.get_key())
            hna_route.interface = iface.get_key()
            hna_route.target = net.network
            hna_route.netmask = iface.netmask
            hna_route.gateway = '0.0.0.0'
            hna_route.table = ROUTING_TABLE_ID

            announced_ifaces.append(iface)
            babel_configured = True

        if has_routing_protocol(manager, 'routing_default_announces') and getattr(manager, 'uplink', False):
            # Add default route announce.
            net = ipaddr.IPNetwork('0.0.0.0/0')
            announced_networks.append(net)

            # For each announced interface add a static route to the Babel routing table.
            hna_route = cfg.network.add(route='babel_rt_%s' % iface.get_key())
            hna_route.interface = iface.get_key()
            hna_route.target = net.network
            hna_route.netmask = '0.0.0.0'
            hna_route.gateway = '0.0.0.0'
            hna_route.table = ROUTING_TABLE_ID

            announced_uplink_ifaces.append(iface)
            babel_configured = True

        if not has_routing_protocol(manager, 'routing_protocols'):
            continue

        if iface.proto == 'none':
            # Configure routable interface to have an IP address if one is not yet
            # assigned as the daemon needs unique addresses on every routable interface.
            try:
                iface.proto = 'static'
                iface.ipaddr = cfg.resources.get(cgm_resources.IpResource, family='ipv4').ip
                iface.netmask = '255.255.255.255'
            except cgm_resources.ResourceExhausted:
                raise cgm_base.ValidationError(_("Not enough IP space to allocate an address for Babel interface!"))

        routable_ifaces.append(iface)
        babel_configured = True

    if not babel_configured:
        return

    general = cfg.babeld.add('general')
    # TODO: Should port be made configurable?
    general.local_port = 33123
    general.ipv6_subtrees = 'true'
    general.export_table = ROUTING_TABLE_ID
    general.import_table = ROUTING_TABLE_ID
    # Disable log file to prevent it filling space.
    general.log_file = '/dev/null'

    # Configure routing table names.
    cfg.routing_tables.set_table(ROUTING_TABLE_NAME, ROUTING_TABLE_ID)
    cfg.routing_tables.set_table(ROUTING_TABLE_DEFAULT_NAME, ROUTING_TABLE_DEFAULT_ID)

    for iface in routable_ifaces:
        interface = cfg.babeld.add('interface')
        interface.ifname = iface.get_key()
        interface.link_quality = 'true'

        # Allow interface-specific routing protocol configuration.
        manager = iface.get_manager()
        if manager is not None:
            signals.cgm_setup_interface.send(
                manager.__class__,
                cfg=cfg,
                manager=manager,
                interface=interface,
            )

        rule = cfg.babeld.add('filter')
        rule.type = 'redistribute'
        rule.local = 'true'
        rule['if'] = iface.get_key()
        rule.action = 'allow'

    for net in announced_networks:
        rule = cfg.babeld.add('filter')
        rule.type = 'redistribute'
        rule.ip = net
        rule.local = 'true'
        # Protocol number '4' means 'static' routes.
        rule.proto = 4
        rule.action = 'allow'

    # Ensure default route is exported into a different table.
    default_route = cfg.babeld.add('filter')
    if cfg.has_package_version('babeld', '1.7.0'):
        default_route.type = 'install'
    else:
        default_route.type = 'export'
    default_route.ip = '0.0.0.0/0'
    default_route.le = 0
    default_route.table = ROUTING_TABLE_DEFAULT_ID

    # By default, do not redistribute any local addresses.
    rule = cfg.babeld.add('filter')
    rule.type = 'redistribute'
    rule.local = 'true'
    rule.action = 'deny'

    # Ensure that all traffic gets routed via the Babel table by default.
    rt = cfg.network.add('rule')
    rt.lookup = ROUTING_TABLE_ID
    rt.priority = ROUTING_TABLE_PRIORITY

    rt = cfg.network.add('rule')
    rt.lookup = ROUTING_TABLE_DEFAULT_ID
    rt.priority = ROUTING_TABLE_DEFAULT_PRIORITY

    # Ensure that forwarding between all Babel interfaces is allowed.
    firewall = cfg.firewall.add('zone', managed_by=BabelProtocolManager())
    firewall.name = 'babel'
    firewall.network = [iface.get_key() for iface in set(routable_ifaces + announced_ifaces)]
    firewall.input = 'ACCEPT'
    firewall.output = 'ACCEPT'
    firewall.forward = 'ACCEPT'

    # Ensure that forwarding between routable interfaces and any uplink interfaces.
    if announced_uplink_ifaces:
        fwd_uplink = cfg.firewall.add('forwarding')
        fwd_uplink.src = firewall.name
        fwd_uplink.dest = 'uplink'

    # Ensure that Babel packages are installed.
    cfg.packages.update([
        'babeld',
        'nodewatcher-agent-mod-routing_babel',
    ])

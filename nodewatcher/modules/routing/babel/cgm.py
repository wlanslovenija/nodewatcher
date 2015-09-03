from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base, resources as cgm_resources
from nodewatcher.utils import ipaddr

from . import models as babel_models

ROUTING_TABLE_ID = 21
ROUTING_TABLE_NAME = 'babel'
ROUTING_TABLE_PRIORITY = 999
ROUTING_TABLE_DEFAULT_ID = 31
ROUTING_TABLE_DEFAULT_NAME = 'babel_default'
ROUTING_TABLE_DEFAULT_PRIORITY = 1099


class BabelProtocolManager(object):
    routing_protocol = babel_models.BABEL_PROTOCOL_NAME


@cgm_base.register_platform_module('openwrt', 900)
def babel(node, cfg):
    babel_configured = False

    # Iterate through interfaces and decide which ones should be included in the routing table. Other
    # modules must have previously set its "_routable" attribute to BABEL_PROTOCOL_NAME.
    routable_ifaces = []
    announced_ifaces = []
    announced_networks = []
    for name, iface in list(cfg.network):
        if iface.get_type() != 'interface':
            continue

        # All interfaces that are marked in _announce for this routing protocol should be redistributed.
        if babel_models.BABEL_PROTOCOL_NAME in (iface._announce or []):
            net = ipaddr.IPNetwork('%s/%s' % (iface.ipaddr, iface.netmask))
            announced_networks.append(net)

            # For each announced interface add a static route to the Babel routing table.
            hna_route = cfg.network.add(route='babel_rt_%s' % iface.get_key())
            hna_route.interface = iface.get_key()
            hna_route.target = net.network
            hna_route.netmask = iface.netmask
            hna_route.gateway = '0.0.0.0'
            hna_route.table = ROUTING_TABLE_ID

            announced_ifaces.append(name)
            babel_configured = True

        if babel_models.BABEL_PROTOCOL_NAME not in (iface._routable or []):
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

        routable_ifaces.append(name)
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
        interface.ifname = iface

        rule = cfg.babeld.add('filter')
        rule.type = 'redistribute'
        rule.local = 'true'
        rule['if'] = iface
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
    firewall.network = list(set(routable_ifaces + announced_ifaces))
    firewall.input = 'ACCEPT'
    firewall.output = 'ACCEPT'
    firewall.forward = 'ACCEPT'

    # Ensure that Babel packages are installed.
    cfg.packages.update([
        'babeld',
        'nodewatcher-agent-mod-routing_babel',
    ])

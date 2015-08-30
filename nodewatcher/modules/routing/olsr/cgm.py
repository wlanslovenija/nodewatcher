from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.generator.cgm import base as cgm_base, resources as cgm_resources
from nodewatcher.utils import ipaddr

from . import models as olsr_models

ROUTING_TABLE_ID = 20
ROUTING_TABLE_NAME = 'olsr'
ROUTING_TABLE_PRIORITY = 1000
ROUTING_TABLE_DEFAULT_ID = 30
ROUTING_TABLE_DEFAULT_NAME = 'olsr_default'
ROUTING_TABLE_DEFAULT_PRIORITY = 1100


class OlsrProtocolManager(object):
    routing_protocol = olsr_models.OLSR_PROTOCOL_NAME


@cgm_base.register_platform_module('openwrt', 900)
def olsr(node, cfg):
    olsrd_configured = False

    # Iterate through interfaces and decide which ones should be included
    # in the routing table; other modules must have previously set its
    # "_routable" attribute to OLSR_PROTOCOL_NAME
    routable_ifaces = []
    announced_ifaces = []
    for name, iface in list(cfg.network):
        if iface.get_type() != 'interface':
            continue

        # All interfaces that are marked in _announce for this routing protocol should be added to HNA
        if olsr_models.OLSR_PROTOCOL_NAME in (iface._announce or []):
            hna = cfg.olsrd.add('Hna4')
            hna.netaddr = ipaddr.IPNetwork('%s/%s' % (iface.ipaddr, iface.netmask)).network
            hna.netmask = iface.netmask

            # For each announced interface add a static route to the OLSR routing table
            hna_route = cfg.network.add(route='olsr_hna_%s' % iface.get_key())
            hna_route.interface = iface.get_key()
            hna_route.target = hna.netaddr
            hna_route.netmask = hna.netmask
            hna_route.gateway = '0.0.0.0'
            hna_route.table = ROUTING_TABLE_ID

            announced_ifaces.append(name)
            olsrd_configured = True

        if olsr_models.OLSR_PROTOCOL_NAME not in (iface._routable or []):
            continue

        if iface.proto == 'none':
            # Configure routable interface to have an IP address if one is not yet
            # assigned as the daemon needs unique addresses on every routable interface
            try:
                iface.proto = 'static'
                iface.ipaddr = cfg.resources.get(cgm_resources.IpResource, family='ipv4').ip
                iface.netmask = '255.255.255.255'
            except cgm_resources.ResourceExhausted:
                raise cgm_base.ValidationError(_("Not enough IP space to allocate an address for OLSR interface!"))

        routable_ifaces.append(name)
        olsrd_configured = True

    if not olsrd_configured:
        return

    olsrd6 = cfg.olsrd6.add('olsrd')
    # TODO: Enable IPv6 configuration for olsrd, currently we just ignore it

    olsrd = cfg.olsrd.add('olsrd')
    olsrd.SrcIpRoutes = 'yes'
    olsrd.RtTable = ROUTING_TABLE_ID
    olsrd.RtTableDefault = ROUTING_TABLE_DEFAULT_ID

    # Configure routing table names
    cfg.routing_tables.set_table(ROUTING_TABLE_NAME, ROUTING_TABLE_ID)
    cfg.routing_tables.set_table(ROUTING_TABLE_DEFAULT_NAME, ROUTING_TABLE_DEFAULT_ID)

    # Configure main IP (router ID)
    try:
        router_id = node.config.core.routerid(queryset=True).get(rid_family='ipv4').router_id
        olsrd.MainIp = router_id
    except core_models.RouterIdConfig.DoesNotExist:
        raise cgm_base.ValidationError(
            _("OLSR routing configured, but router ID is missing! In order to use OLSR, the node must have a configured primary IP address.")
        )

    if routable_ifaces:
        iface = cfg.olsrd.add('Interface')
        iface.interface = routable_ifaces
        iface.IPv4Multicast = '255.255.255.255'

    # Ensure that all traffic gets routed via the olsrd table by default
    rt = cfg.network.add('rule')
    rt.lookup = ROUTING_TABLE_ID
    rt.priority = ROUTING_TABLE_PRIORITY

    rt = cfg.network.add('rule')
    rt.lookup = ROUTING_TABLE_DEFAULT_ID
    rt.priority = ROUTING_TABLE_DEFAULT_PRIORITY

    # Ensure that forwarding between all OLSR interfaces is allowed
    firewall = cfg.firewall.add('zone', managed_by=OlsrProtocolManager())
    firewall.name = 'olsr'
    firewall.network = list(set(routable_ifaces + announced_ifaces))
    firewall.input = 'ACCEPT'
    firewall.output = 'ACCEPT'
    firewall.forward = 'ACCEPT'

    # Enable jsoninfo plugin.
    jsoninfo = cfg.olsrd.add('LoadPlugin')
    jsoninfo.library = 'olsrd_jsoninfo.so.0.0'

    # Ensure that OLSR packages are installed.
    cfg.packages.update([
        'olsrd',
        'olsrd-mod-jsoninfo',
        'nodewatcher-agent-mod-routing_olsr',
    ])


@cgm_base.register_platform_package('openwrt', 'olsrd-mod-txtinfo', olsr_models.OlsrdModTxtinfoPackageConfig)
def olsrd_mod_txtinfo_package(node, pkgcfg, cfg):
    """
    Configures the olsrd-mod-txtinfo package.
    """

    # We only take the first package configuration into account and ignore the rest
    pkgcfg = pkgcfg[0]

    # TODO: Also support IPv6 olsrd configuration

    plugin = cfg.olsrd.add('LoadPlugin')
    plugin.library = 'olsrd_txtinfo.so.0.1'
    plugin.port = pkgcfg.port
    plugin.accept = str(pkgcfg.allowed_host.ip)

from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.generator.cgm import base as cgm_base, resources as cgm_resources
from nodewatcher.utils import ipaddr

from . import models as olsr_models

ROUTING_TABLE_ID = 20
ROUTING_TABLE_NAME = 'olsr'
ROUTING_TABLE_PRIORITY = 1000


@cgm_base.register_platform_module('openwrt', 900)
def olsr(node, cfg):
    try:
        router_id = node.config.core.routerid(queryset=True).get(family='ipv4').router_id
    except core_models.RouterIdConfig.DoesNotExist:
        return

    olsrd = cfg.olsrd.add('olsrd')
    olsrd.IpVersion = 4
    olsrd.AllowNoInt = 'yes'
    olsrd.UseHysteresis = 'no'
    olsrd.LinkQualityFishEye = '0'
    olsrd.Willingness = 3
    olsrd.LinkQualityLevel = 2
    olsrd.LinkQualityAging = '0.1'
    olsrd.LinkQualityAlgorithm = 'etx_ff'
    olsrd.FIBMetric = 'flat'
    olsrd.Pollrate = '0.025'
    olsrd.TcRedundancy = 2
    olsrd.MprCoverage = 3
    olsrd.NatThreshold = '0.75'
    olsrd.SmartGateway = 'no'
    olsrd.MainIp = router_id
    olsrd.SrcIpRoutes = 'yes'
    olsrd.RtTable = ROUTING_TABLE_ID

    # Iterate through interfaces and decide which ones should be included
    # in the routing table; other modules must have previously set its
    # "_routable" attribute to OLSR_PROTOCOL_NAME
    routable_ifaces = []
    for name, iface in cfg.network:
        # All interfaces that are marked in _announce for this routing protocol should be added to HNA
        if olsr_models.OLSR_PROTOCOL_NAME in (iface._announce or []):
            hna = cfg.olsrd.add('Hna4')
            hna.netaddr = ipaddr.IPNetwork('%s/%s' % (iface.ipaddr, iface.netmask)).network
            hna.netmask = iface.netmask

        if iface._routable != olsr_models.OLSR_PROTOCOL_NAME:
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

    if routable_ifaces:
        iface = cfg.olsrd.add('Interface')
        iface.interface = routable_ifaces
        iface.IPv4Multicast = '255.255.255.255'
        iface.HelloInterval = '5.0'
        iface.HelloValidityTime = '40.0'
        iface.TcInterval = '7.0'
        iface.TcValidityTime = '161.0'
        iface.MidInterval = '18.0'
        iface.MidValidityTime = '324.0'
        iface.HnaInterval = '18.0'
        iface.HnaValidityTime = '324.0'

    # Create the olsrd routing table
    rt = cfg.routing.add(table=ROUTING_TABLE_NAME)
    rt.id = ROUTING_TABLE_ID

    # Ensure that all traffic gets routed via the olsrd table by default
    rt = cfg.routing.add('policy')
    rt.table = ROUTING_TABLE_NAME
    rt.priority = ROUTING_TABLE_PRIORITY

    # Support policy routing configuration in trunk
    rt = cfg.network.add('rule')
    rt.lookup = ROUTING_TABLE_ID
    rt.priority = ROUTING_TABLE_PRIORITY

    # Ensure that "olsrd" and "policy-routing" packages are installed
    cfg.packages.update(['olsrd', 'policy-routing'])

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

            # Configure DHCP for client network class.
            dhcp = cfg.dhcp.add(dhcp=name)
            dhcp.interface = name
            dhcp.start = 2
            dhcp.limit = 150
            dhcp.leasetime = 900
            dhcp.ignore = False
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

    # Configure DHCP defaults.
    dnsmasq = cfg.dhcp.find_ordered_section('dnsmasq')
    dnsmasq.domainneeded = True
    dnsmasq.boguspriv = True
    dnsmasq.filterwin2k = False
    dnsmasq.localise_queries = True
    dnsmasq.rebind_protection = True
    dnsmasq.rebind_localhost = True
    dnsmasq.local = '/mesh.local/'
    dnsmasq.domain = 'mesh.local'
    dnsmasq.expandhosts = True
    dnsmasq.nonegcache = False
    dnsmasq.authoritative = True
    dnsmasq.readethers = True
    dnsmasq.leasefile = '/tmp/dhcp.leases'
    dnsmasq.resolvfile = '/tmp/resolv.conf.auto'
    dnsmasq.addnhosts = ['/var/run/hosts_olsr']

    # Configure uhttpd defaults.
    uhttpd = cfg.uhttpd.add(uhttpd='main')
    uhttpd.listen_http = ['0.0.0.0:80']
    uhttpd.listen_https = ['0.0.0.0:443']
    uhttpd.home = '/www'
    uhttpd.rfc1918_filter = False
    uhttpd.max_requests = 2
    uhttpd.cert = '/etc/uhttpd.crt'
    uhttpd.key = '/etc/uhttpd.key'
    uhttpd.cgi_prefix = '/cgi-bin'
    uhttpd.script_timeout = 300
    uhttpd.network_timeout = 30
    uhttpd.tcp_keepalive = True

    cert = cfg.uhttpd.add(cert='px5g')
    cert.days = '730'
    cert.bits = '2048'
    cert.country = 'US'
    cert.state = 'DC'
    cert.location = 'Washington'
    cert.commonname = 'Commotion'

    # Configure olsrd defaults.
    olsrd = cfg.olsrd.add('olsrd')
    olsrd.IpVersion = 4
    olsrd.LinkQualityLevel = 2
    olsrd.LinkQualityAlgorithm = 'etx_ffeth'
    olsrd.SmartGateway = 'yes'
    cfg.packages.add('olsrd')

    plugin = cfg.olsrd.add('LoadPlugin')
    plugin.library = 'olsrd_arprefresh.so.0.1'
    cfg.packages.add('olsrd-mod-arprefresh')

    plugin = cfg.olsrd.add('LoadPlugin')
    plugin.library = 'olsrd_dyn_gw_plain.so.0.4'
    cfg.packages.add('olsrd-mod-dyn-gw-plain')

    plugin = cfg.olsrd.add('LoadPlugin')
    plugin.library = 'olsrd_nameservice.so.0.3'
    plugin.sighup_pid_file = '/var/run/dnsmasq.pid'
    plugin.hosts_file = '/var/run/hosts_olsr'
    plugin.suffix = '.mesh.local'
    cfg.packages.add('olsrd-mod-nameservice')

    plugin = cfg.olsrd.add('LoadPlugin')
    plugin.library = 'olsrd_dnssd.so.0.1.3'
    plugin.P2pdTtl = 5
    plugin.UdpDestPort = '224.0.0.251 5353'
    plugin.ServiceFileDir = '/etc/avahi/services'
    plugin.Domain = 'mesh.local'
    plugin.ServiceUpdateInterval = 300
    cfg.packages.add('olsrd-mod-dnssd')

    plugin = cfg.olsrd.add('LoadPlugin')
    plugin.library = 'olsrd_txtinfo.so.0.1'
    plugin.accept = '127.0.0.1'
    plugin.listen = '127.0.0.1'
    cfg.packages.add('olsrd-mod-txtinfo')

    plugin = cfg.olsrd.add('LoadPlugin')
    plugin.library = 'olsrd_jsoninfo.so.0.0'
    plugin.accept = '127.0.0.1'
    plugin.listen = '127.0.0.1'
    plugin.port = 9090
    plugin.UUIDFile = '/etc/olsrd.d/olsrd.uuid'
    cfg.packages.add('olsrd-mod-jsoninfo')

    # Ensure commotion packages are installed.
    cfg.packages.update([
        'commotion',
        'commotion-gui',
    ])

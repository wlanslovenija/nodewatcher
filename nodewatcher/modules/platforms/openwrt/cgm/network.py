from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.allocation.ip import models as pool_models
from nodewatcher.core.generator.cgm import models as cgm_models, base as cgm_base, resources as cgm_resources, devices as cgm_devices

# NAT routing table.
NAT_ROUTING_TABLE_ID = 100
NAT_ROUTING_TABLE_NAME = 'nat'
NAT_ROUTING_TABLE_PRIORITY = 600


@cgm_base.register_platform_module('openwrt', 1)
def router_id(node, cfg):
    """
    Registers all router identifiers for use by routing CGMs.
    """

    for rid in node.config.core.routerid():
        if isinstance(rid, core_models.StaticIpRouterIdConfig):
            res = cgm_resources.IpResource(rid.rid_family, rid.address, rid, allow_broadcast=True)
            cfg.resources.add(res)
        elif isinstance(rid, pool_models.AllocatedIpRouterIdConfig):
            # Check that the network has actually been allocated and fail validation if not so
            if not rid.allocation:
                raise cgm_base.ValidationError(_("Missing network allocation in router ID configuration."))

            res = cgm_resources.IpResource(rid.family, rid.allocation.ip_subnet, rid, allow_broadcast=True)
            cfg.resources.add(res)


def configure_leasable_network(cfg, node, interface, network, iface_name, subnet):
    """
    A helper function to configure network lease.

    :param cfg: Platform configuration
    :param node: Node instance
    :param interface: Interface configuration
    :param network: Network configuration
    :param iface_name: Name of the UCI interface
    :param subnet: Subnet to be leased
    """

    if network.lease_type == 'dhcp':
        try:
            dhcp = cfg.dhcp.add(dhcp=iface_name)
            dhcp.interface = iface_name
        except ValueError:
            dhcp = cfg.dhcp[iface_name]

        dhcp.start = 2
        dhcp.limit = len(list(subnet.iterhosts())) - 1
        dhcp.leasetime = int(network.lease_duration.total_seconds())

    if network.nat_type == 'snat-routed-networks':
        # SNAT using the primary router identifier as source address.
        try:
            router_id = node.config.core.routerid(queryset=True).filter(rid_family='ipv4')[0].router_id
        except IndexError:
            raise cgm_base.ValidationError(
                _("SNAT towards routed networks configured, but router ID is missing! The node must have a configured primary IP address.")
            )

        if getattr(network, 'routing_announces', []) or getattr(interface, 'routing_protocols', []):
            raise cgm_base.ValidationError(
                _("NAT may not be used together with routing on the same interface.")
            )

        # Create a firewall zone for this interface so we can use it as source.
        zone = cfg.firewall.add('zone')
        zone.name = iface_name
        zone.network = [iface_name]
        zone.input = 'ACCEPT'
        zone.output = 'ACCEPT'
        zone.forward = 'ACCEPT'
        zone.conntrack = True

        # Add policy routing to route traffic towards the network.
        cfg.routing_tables.set_table(NAT_ROUTING_TABLE_NAME, NAT_ROUTING_TABLE_ID)

        if not cfg.network.find_ordered_section('rule', lookup=NAT_ROUTING_TABLE_ID):
            policy = cfg.network.add('rule')
            policy.lookup = NAT_ROUTING_TABLE_ID
            policy.priority = NAT_ROUTING_TABLE_PRIORITY

        nat_route = cfg.network.add(route='nat_%s' % iface_name)
        nat_route.interface = iface_name
        nat_route.target = subnet.network
        nat_route.netmask = subnet.netmask
        nat_route.gateway = '0.0.0.0'
        nat_route.table = NAT_ROUTING_TABLE_ID

        # Setup NAT towards routed networks. Since the routing protocol modules have probably
        # not yet been configured, we wait until later to configure this.
        @cfg.defer_configuration
        def nat_routed_networks():
            for zone in cfg.firewall.find_all_ordered_sections('zone'):
                # Enable connection tracking on all the zones. If we don't do this, NAT may not
                # work as the firewall will disable connection tracking on some devices even when
                # they are part of other zones which require connection tracking.
                # See OpenWrt ticket: https://dev.openwrt.org/ticket/20374
                zone.conntrack = True

                # Ignore zones which are not managed by routing protocols.
                if not hasattr(zone.get_manager(), 'routing_protocol'):
                    continue

                # Create a SNAT rule.
                redirect = cfg.firewall.add('redirect')
                redirect.src = iface_name
                redirect.dest = zone.name
                redirect.src_ip = str(subnet)
                redirect.src_dip = router_id
                redirect.proto = 'all'
                redirect.target = 'SNAT'

                # Allow forwarding in both directions.
                forward_in = cfg.firewall.add('forwarding')
                forward_in.src = zone.name
                forward_in.dest = iface_name

                forward_out = cfg.firewall.add('forwarding')
                forward_out.src = iface_name
                forward_out.dest = zone.name


def configure_network(cfg, node, interface, network, section, iface_name):
    """
    A helper function to configure an interface's network.

    :param cfg: Platform configuration
    :param node: Node instance
    :param interface: Interface configuration
    :param network: Network configuration
    :param section: UCI interface or alias section
    :param iface_name: Name of the UCI interface
    """

    section.add_manager(network)

    if isinstance(network, cgm_models.StaticNetworkConfig):
        section.proto = 'static'
        if network.family == 'ipv4':
            section.ipaddr = network.address.ip
            section.netmask = network.address.netmask
            if network.gateway:
                section.gateway = network.gateway.ip
        elif network.family == 'ipv6':
            section.ip6addr = network.address
            if network.gateway:
                section.ip6gw = network.gateway.ip
        else:
            raise cgm_base.ValidationError(_("Unsupported address family '%s'!") % network.family)

        configure_leasable_network(cfg, node, interface, network, iface_name, network.address)
    elif isinstance(network, cgm_models.AllocatedNetworkConfig):
        section.proto = 'static'

        # Check that the network has actually been allocated and fail validation if not so
        if not network.allocation:
            raise cgm_base.ValidationError(_("Missing network allocation."))

        if network.family in ('ipv4', 'ipv6'):
            res = cgm_resources.IpResource(network.family, network.allocation.ip_subnet, network)
            address = res.allocate()

            if network.family == 'ipv4':
                section.ipaddr = address.ip
                section.netmask = address.netmask
            elif network.family == 'ipv6':
                section.ip6addr = address

            configure_leasable_network(cfg, node, interface, network, iface_name, address)
        else:
            raise cgm_base.ValidationError(_("Unsupported address family '%s'!") % network.family)
    elif isinstance(network, cgm_models.DHCPNetworkConfig):
        section.proto = 'dhcp'
        section.hostname = cfg.system.system[0].hostname
        section.peerdns = network.dns
        section.defaultroute = network.default_route
    elif isinstance(network, cgm_models.PPPoENetworkConfig):
        section.proto = 'pppoe'
        section.username = network.username
        section.password = network.password

        # Add required packages for using PPPoE.
        cfg.packages.update([
            'kmod-pppoe',
            'ppp-mod-pppoe',
            'ppp'
        ])
    else:
        section.proto = 'none'


def configure_interface(cfg, node, interface, section, iface_name):
    """
    A helper function to configure an interface.

    :param cfg: Platform configuration
    :param node: Node instance
    :param interface: Interface configuration
    :param section: UCI interface section
    :param iface_name: Name of the UCI interface
    """

    networks = [x.cast() for x in interface.networks.all()]
    if networks:
        network = networks[0]
        configure_network(cfg, node, interface, network, section, iface_name)

        # Additional network configurations are aliases.
        for network in networks[1:]:
            alias = cfg.network.add('alias', managed_by=interface)
            alias.interface = iface_name
            configure_network(cfg, node, interface, network, alias, iface_name)
    else:
        section.proto = 'none'

    # Configure uplink interface.
    if getattr(interface, 'uplink', None):
        section._uplink = True
        set_dhcp_ignore(cfg, iface_name)

        # An uplink interface cannot be used for routing.
        if getattr(interface, 'routing_protocols', []):
            raise cgm_base.ValidationError(_("An uplink interface cannot also be used for routing!"))

        # Configure firewall policy for the uplink interface.
        firewall = cfg.firewall.find_ordered_section('zone', name='uplink')
        if not firewall:
            firewall = cfg.firewall.add('zone')
            firewall.name = 'uplink'
            firewall.input = 'DROP'
            firewall.output = 'ACCEPT'
            firewall.forward = 'REJECT'

            # Ensure DHCP client is allowed on the uplink interface.
            dhcp_rule = cfg.firewall.add('rule')
            dhcp_rule.src = 'uplink'
            dhcp_rule.proto = 'udp'
            dhcp_rule.src_port = 67
            dhcp_rule.dest_port = 68
            dhcp_rule.target = 'ACCEPT'

            # Ensure ICMP traffic is allowed on the uplink interface.
            icmp_rule = cfg.firewall.add('rule')
            icmp_rule.src = 'uplink'
            icmp_rule.proto = 'icmp'
            icmp_rule.target = 'ACCEPT'

        if not firewall.network:
            firewall.network = []

        firewall.network.append(iface_name)

        if getattr(interface, 'routing_default_announces', []):
            # Configure masquerade if a default route is announced via this interface
            # for any routing protocol.
            firewall.masq = True
            firewall.mtu_fix = True
        else:
            # Ensure that uplink traffic is routed via the main table.
            policy = cfg.network.add('rule')
            policy['in'] = iface_name
            policy.lookup = 'main'
            policy.priority = 500


def configure_switch(cfg, device, switch, vlan):
    """
    Configures a switch port.

    :param cfg: Platform configuration
    :param device: Device descriptor
    :param switch: Switch descriptor
    :param vlan: VLAN configuration
    """

    switch_iface = device.remap_port(cfg.platform, switch.identifier)
    if switch_iface is None:
        raise cgm_base.ValidationError(
            _("No mapping for OpenWrt when configuring switch '%(switch)s'.") % {'switch': switch.identifier}
        )

    # Enable switch if not yet enabled.
    try:
        sw = cfg.network.add(switch=switch_iface)
        sw.enable_vlan = True
    except ValueError:
        # Switch is already enabled.
        pass

    # Check if wanted VLAN is already configured.
    if 'switch_vlan' in cfg.network:
        for existing_vlan in cfg.network.switch_vlan:
            if existing_vlan.device == switch_iface and existing_vlan.vlan == vlan.vlan:
                raise cgm_base.ValidationError(_("VLAN assignment conflict while trying to configure switch!"))

    # Configure VLAN.
    vlan_cfg = cfg.network.add('switch_vlan')
    vlan_cfg.device = switch_iface
    vlan_cfg.vlan = vlan.vlan
    ports = []
    for p in vlan.ports:
        if switch.is_tagged(p):
            p = '%st' % p
        ports.append(str(p))
    vlan_cfg.ports = ' '.join(ports)


def set_dhcp_ignore(cfg, iface_name):
    """
    Ensure that DHCP server does not announce anything via an interface.

    :param cfg: UCI configuration instance
    :param iface_name: Interface name
    """

    try:
        iface_dhcp = cfg.dhcp.add(dhcp=iface_name)
        iface_dhcp.interface = iface_name
    except ValueError:
        iface_dhcp = cfg.dhcp[iface_name]

    iface_dhcp.ignore = True


def check_interface_bridged(interface):
    """
    Checks if the interface is part of a bridge and returns the bridge
    descriptor if so.

    :param interface: Interface instance
    :return: Bridge interface or None if interface is not part of a bridge
    """

    bridge = None
    for network in interface.networks.all():
        if isinstance(network, cgm_models.BridgedNetworkConfig):
            if bridge is not None:
                raise cgm_base.ValidationError(
                    _("Interface cannot be part of multiple bridges!")
                )

            bridge = network.bridge
            if bridge is None:
                raise cgm_base.ValidationError(
                    _("Bridge interface cannot be empty!")
                )
        elif bridge is not None:
            raise cgm_base.ValidationError(
                _("Interface cannot be part of a bridge and also have network configuration!")
            )

    return bridge


@cgm_base.register_platform_module('openwrt', 15)
def network(node, cfg):
    """
    Basic network configuration.
    """

    lo = cfg.network.add(interface='loopback')
    lo.ifname = 'lo'
    lo.proto = 'static'
    lo.ipaddr = '127.0.0.1'
    lo.netmask = '255.0.0.0'

    # Ensure the IPv4 address for the router ID is assigned to loopback.
    try:
        router_id = node.config.core.routerid(queryset=True).filter(rid_family='ipv4')[0].router_id

        lo_rid = cfg.network.add(alias='routerid')
        lo_rid.interface = 'loopback'
        lo_rid.proto = 'static'
        lo_rid.ipaddr = router_id
        lo_rid.netmask = '255.255.255.255'
    except IndexError:
        pass

    # Configure default routing table names.
    cfg.routing_tables.set_table('local', 255)
    cfg.routing_tables.set_table('main', 254)
    cfg.routing_tables.set_table('default', 253)
    cfg.routing_tables.set_table('unspec', 0)

    # Configure IPv4 defaults.
    cfg.sysctl.set_variable('net.ipv4.conf.default.arp_ignore', 1)
    cfg.sysctl.set_variable('net.ipv4.conf.all.arp_ignore', 1)
    cfg.sysctl.set_variable('net.ipv4.icmp_echo_ignore_broadcasts', 1)
    cfg.sysctl.set_variable('net.ipv4.icmp_ignore_bogus_error_responses', 1)
    cfg.sysctl.set_variable('net.ipv4.igmp_max_memberships', 100)
    cfg.sysctl.set_variable('net.ipv4.tcp_ecn', 0)
    cfg.sysctl.set_variable('net.ipv4.tcp_fin_timeout', 30)
    cfg.sysctl.set_variable('net.ipv4.tcp_keepalive_time', 120)
    cfg.sysctl.set_variable('net.ipv4.tcp_syncookies', 1)
    cfg.sysctl.set_variable('net.ipv4.tcp_timestamps', 1)
    cfg.sysctl.set_variable('net.ipv4.tcp_sack', 1)
    cfg.sysctl.set_variable('net.ipv4.tcp_dsack', 1)

    # Enable forwarding for IPv4 and IPv6.
    cfg.sysctl.set_variable('net.ipv4.ip_forward', 1)
    cfg.sysctl.set_variable('net.ipv6.conf.default.forwarding', 1)
    cfg.sysctl.set_variable('net.ipv6.conf.all.forwarding', 1)

    # Ensure IPv6 DAD (Duplicate Address Detection) is disabled as it may cause problems.
    cfg.sysctl.set_variable('net.ipv6.conf.default.accept_dad', 0)
    cfg.sysctl.set_variable('net.ipv6.conf.all.accept_dad', 0)

    # Obtain the device descriptor for this device.
    device = node.config.core.general().get_device()
    if not device:
        return

    # Configure switches.
    vlan_ports = []
    for switch in node.config.core.switch():
        switch_descriptor = device.get_switch(switch.switch)

        for vlan in switch.vlans.all():
            vlan_ports.append(switch_descriptor.get_port_identifier(vlan.vlan))
            configure_switch(cfg, device, switch_descriptor, vlan)

    # Generate physical port resource so we can track binding of ports to different
    # interface and prevent multiple definitions.
    cfg.resources.add(cgm_resources.PhysicalPortResource(
        'ethernet',
        [port.identifier for port in device.ports] + vlan_ports,
    ))
    cfg.resources.add(cgm_resources.PhysicalPortResource(
        'radio',
        [radio.identifier for radio in device.radios],
    ))

    # Include iproute package.
    cfg.packages.add('ip')

    # Configure all interfaces.
    for interface in node.config.core.interfaces():
        if not interface.enabled:
            continue

        if isinstance(interface, cgm_models.BridgeInterfaceConfig):
            iface_name = cfg.sanitize_identifier(device.get_bridge_mapping(cfg.platform, interface))
            iface = cfg.network.add(interface=iface_name, managed_by=interface)
            iface.type = 'bridge'

            # Configure bridge interfaces.
            iface.ifname = []
            for port in interface.bridge_ports.all():
                port = port.interface
                if isinstance(port, cgm_models.EthernetInterfaceConfig):
                    raw_port = device.remap_port(cfg.platform, port.eth_port)
                    if raw_port is None:
                        raise cgm_base.ValidationError(
                            _("No port remapping for port '%(port)s' of device '%(device_name)s' is available!") % {
                                'port': port.eth_port,
                                'device_name': device.name
                            }
                        )
                    elif isinstance(raw_port, (list, tuple)):
                        iface.ifname += raw_port
                    else:
                        iface.ifname.append(raw_port)

                    if port.routing_protocols:
                        raise cgm_base.ValidationError(
                            _("Ethernet interface '%(name)s' cannot be part of a bridge and also marked as routable!") % {
                                'name': port.eth_port,
                            }
                        )
                elif isinstance(port, cgm_models.WifiInterfaceConfig):
                    # Wireless interfaces are reverse-configured to be part of a bridge
                    if port.routing_protocols:
                        raise cgm_base.ValidationError(
                            _("Wireless interface under radio '%(radio)s' cannot be part of a bridge and also marked as routable!") % {
                                'radio': port.device.wifi_radio,
                            }
                        )
                else:
                    raise cgm_base.ValidationError(
                        _("Unsupported interface type '%(type)s' used as bridge port!" % {'type': port.interface.__class__.__name__})
                    )

            iface.stp = interface.stp
            if interface.mac_address:
                iface.macaddr = interface.mac_address

            configure_interface(cfg, node, interface, iface, iface_name)
        elif isinstance(interface, cgm_models.MobileInterfaceConfig):
            # Check if the device actually supports USB.
            if not device.usb:
                raise cgm_base.ValidationError(
                    _("The target device does not support USB, so mobile interface cannot be configured!")
                )

            iface_name = cfg.sanitize_identifier(interface.device)
            iface = cfg.network.add(interface=iface_name, managed_by=interface)

            if interface.device.startswith('eth'):
                # Mobile modem presents itself as a USB ethernet device. Determine the port based on
                # the existing device port map to see which interfaces are already there by default.
                used_ports = set()
                for port in device.get_port_map(cfg.platform).values():
                    if isinstance(port, cgm_devices.SwitchPortMap):
                        port = port.get_port(vlan=0)
                    if not port.startswith('eth'):
                        continue

                    port = port.split('.')[0]
                    used_ports.add(int(port[3:]))

                for port_base in xrange(10):
                    if port_base not in used_ports:
                        break
                else:
                    raise cgm_base.ValidationError(
                        _("Unable to determine free ethernet port for mobile interface '%(port)s'!") % {'port': interface.device}
                    )

                # TODO: Handle these as resources.
                port_map = {
                    'eth-cdc0': 'eth%d' % (port_base + 0),
                    'eth-cdc1': 'eth%d' % (port_base + 1),
                    'eth-cdc2': 'eth%d' % (port_base + 2),
                }

                iface.ifname = port_map.get(interface.device, None)
                if not iface.ifname:
                    raise cgm_base.ValidationError(
                        _("Unsupported mobile interface port '%(port)s'!") % {'port': interface.device}
                    )

                configure_interface(cfg, node, interface, iface, iface_name)
                iface.proto = 'dhcp'

                cfg.packages.update([
                    'kmod-usb-net-cdc-ether',
                ])
            else:
                # Mapping of device identifiers to ports.
                # TODO: Handle these as resources.
                port_map = {
                    'ppp0': '/dev/ttyUSB0',
                    'ppp1': '/dev/ttyUSB1',
                    'ppp2': '/dev/ttyUSB2',
                    'ppp3': '/dev/ttyUSB3',
                    'qmi0': '/dev/cdc-wdm0',
                    'qmi1': '/dev/cdc-wdm1',
                    'qmi2': '/dev/cdc-wdm2',
                }

                iface.device = port_map.get(interface.device, None)
                if not iface.device:
                    raise cgm_base.ValidationError(
                        _("Unsupported mobile interface port '%(port)s'!") % {'port': interface.device}
                    )

                if interface.service == 'umts':
                    iface.service = 'umts'
                elif interface.service == 'gprs':
                    iface.service = 'gprs'
                elif interface.service == 'cdma':
                    iface.service = 'cdma'
                else:
                    raise cgm_base.ValidationError(
                        _("Unsupported mobile service type '%(service)s'!") % {'service': interface.service}
                    )

                iface.apn = interface.apn
                if iface.pincode:
                    iface.pincode = interface.pin
                if interface.username:
                    iface.username = interface.username
                    iface.password = interface.password

                configure_interface(cfg, node, interface, iface, iface_name)
                if interface.device.startswith('ppp'):
                    iface.proto = '3g'
                elif interface.device.startswith('qmi'):
                    iface.proto = 'qmi'

                    cfg.packages.update([
                        'kmod-mii',
                        'kmod-usb-net',
                        'kmod-usb-wdm',
                        'kmod-usb-net-qmi-wwan',
                        'uqmi',
                    ])
                else:
                    raise cgm_base.ValidationError(
                        _("Unsupported mobile interface type '%(port)s'!") % {'port': interface.device}
                    )

            # Some packages are required for using a mobile interface.
            cfg.packages.update([
                'comgt',
                'usb-modeswitch',
                'kmod-usb-serial',
                'kmod-usb-serial-option',
                'kmod-usb-serial-wwan',
                'kmod-usb-acm',
            ])
        elif isinstance(interface, cgm_models.EthernetInterfaceConfig):
            # Allocate the port to ensure it is only bound to this interface.
            try:
                cfg.resources.get(cgm_resources.PhysicalPortResource, port_type='ethernet', port=interface.eth_port)
            except cgm_resources.ResourceExhausted:
                raise cgm_base.ValidationError(
                    _("Ethernet port '%(name)s' cannot be bound to multiple interfaces.") % {
                        'name': interface.eth_port,
                    }
                )

            if check_interface_bridged(interface) is not None:
                continue

            iface_name = cfg.sanitize_identifier(interface.eth_port)

            try:
                iface = cfg.network.add(interface=iface_name, managed_by=interface)
            except ValueError:
                raise cgm_base.ValidationError(
                    _("Duplicate interface definition for port '%s'!") % interface.eth_port
                )

            iface.ifname = device.remap_port(cfg.platform, interface.eth_port)
            if iface.ifname is None:
                raise cgm_base.ValidationError(
                    _("No port remapping for port '%(port)s' of device '%(device_name)s' is available!") % {
                        'port': interface.eth_port,
                        'device_name': device.name
                    }
                )

            if isinstance(iface.ifname, (list, tuple)):
                iface.type = 'bridge'

            if interface.mac_address:
                iface.macaddr = interface.mac_address

            configure_interface(cfg, node, interface, iface, iface_name)
        elif isinstance(interface, cgm_models.WifiRadioDeviceConfig):
            # Allocate the port to ensure it is only bound to this bridge.
            try:
                cfg.resources.get(cgm_resources.PhysicalPortResource, port_type='radio', port=interface.wifi_radio)
            except cgm_resources.ResourceExhausted:
                raise cgm_base.ValidationError(
                    _("Wireless radio '%(name)s' cannot be bound to multiple interfaces.") % {
                        'name': interface.wifi_radio,
                    }
                )

            # Configure virtual interfaces on top of the same radio device.
            dsc_radio = device.get_radio(interface.wifi_radio)
            interfaces = list(interface.interfaces.filter(enabled=True))
            if len(interfaces) > 1 and not dsc_radio.has_feature(cgm_devices.DeviceRadio.MultipleSSID):
                raise cgm_base.ValidationError(_("Router '%s' does not support multiple SSIDs!") % device.name)

            if isinstance(dsc_radio, cgm_devices.IntegratedRadio):
                # Integrated radios have specified names and drivers.
                wifi_radio = device.remap_port(cfg.platform, interface.wifi_radio)
                if not wifi_radio:
                    raise cgm_base.ValidationError(
                        _("Radio '%s' not defined on OpenWRT!") % interface.wifi_radio
                    )

                try:
                    radio_type = device.get_driver(cfg.platform, interface.wifi_radio)
                except KeyError:
                    raise cgm_base.ValidationError(
                        _("Radio driver for '%s' not defined on OpenWRT!") % interface.wifi_radio
                    )
            elif isinstance(dsc_radio, cgm_devices.USBRadio):
                wifi_radio = 'radio%d' % dsc_radio.index
                radio_type = 'mac80211'

                # Add required packages.
                # TODO: This currently assumes an ath9k radio.
                cfg.packages.update([
                    'kmod-ath9k-htc',
                    'kmod-ath9k-common',
                ])
            else:
                raise cgm_base.ValidationError(
                    _("Radio type '%s' not supported on OpenWRT!") % dsc_radio.__class__.__name__
                )

            try:
                radio = cfg.wireless.add(**{'wifi-device': wifi_radio})
            except ValueError:
                raise cgm_base.ValidationError(
                    _("Duplicate radio definition for radio '%s'!") % interface.wifi_radio
                )

            radio.type = radio_type
            dsc_protocol = dsc_radio.get_protocol(interface.protocol)
            dsc_channel = dsc_protocol.get_channel(interface.channel) if interface.channel else None
            dsc_channel_width = dsc_protocol.get_channel_width(interface.channel_width)

            # Select proper hardware mode
            if dsc_protocol.identifier in ('ieee-80211bg', 'ieee-80211bgn'):
                radio.hwmode = '11g'
            elif dsc_protocol.identifier in ('ieee-80211a', 'ieee-80211an', 'ieee-80211ac'):
                radio.hwmode = '11a'
            else:
                raise cgm_base.ValidationError(_("Unsupported OpenWRT wireless protocol '%s'!") % dsc_protocol.identifier)

            # Select proper channel width
            if dsc_protocol.identifier in ('ieee-80211bg', 'ieee-80211a'):
                if dsc_channel_width.identifier == 'nw5':
                    radio.chanbw = 5
                elif dsc_channel_width.identifier == 'nw10':
                    radio.chanbw = 10
                elif dsc_channel_width.identifier == 'ht20':
                    radio.chanbw = 20
                else:
                    raise cgm_base.ValidationError(_("Unsupported OpenWRT channel width '%s'!") % dsc_channel_width.identifier)
            elif dsc_protocol.identifier in ('ieee-80211bgn', 'ieee-80211an'):
                if dsc_channel_width.identifier == 'nw5':
                    radio.htmode = 'HT20'
                    radio.chanbw = 5
                elif dsc_channel_width.identifier == 'nw10':
                    radio.htmode = 'HT20'
                    radio.chanbw = 10
                elif dsc_channel_width.identifier == 'ht20':
                    radio.htmode = 'HT20'
                elif dsc_channel_width.identifier == 'ht40l':
                    radio.htmode = 'HT40-'
                elif dsc_channel_width.identifier == 'ht40u':
                    radio.htmode = 'HT40+'
                else:
                    raise cgm_base.ValidationError(_("Unsupported OpenWRT channel width '%s'!") % dsc_channel_width.identifier)
                radio.ht_capab = []

                for capability in dsc_protocol.available_capabilities:
                    radio.ht_capab.append(capability.identifier)
            elif dsc_protocol.identifier in ('ieee-80211ac',):
                if dsc_channel_width.identifier == 'nw5':
                    radio.htmode = 'VHT20'
                    radio.chanbw = 5
                elif dsc_channel_width.identifier == 'nw10':
                    radio.htmode = 'VHT20'
                    radio.chanbw = 10
                elif dsc_channel_width.identifier == 'ht20':
                    radio.htmode = 'VHT20'
                elif dsc_channel_width.identifier == 'ht40':
                    radio.htmode = 'VHT40'
                elif dsc_channel_width.identifier == 'ht80':
                    radio.htmode = 'VHT80'
                elif dsc_channel_width.identifier == 'ht160':
                    radio.htmode = 'VHT160'
                else:
                    raise cgm_base.ValidationError(_("Unsupported OpenWRT channel width '%s'!") % dsc_channel_width.identifier)
                radio.ht_capab = []

                for capability in dsc_protocol.available_capabilities:
                    radio.ht_capab.append(capability.identifier)
            else:
                raise cgm_base.ValidationError(_("Unsupported OpenWRT wireless protocol '%s'!") % dsc_protocol.identifier)

            radio.phy = 'phy%d' % dsc_radio.index
            radio.channel = dsc_channel.number if dsc_channel is not None else 'auto'
            if interface.ack_distance:
                radio.distance = interface.ack_distance
            if interface.tx_power:
                radio.txpower = interface.tx_power

            for vif in interfaces:
                wif = cfg.wireless.add('wifi-iface')
                wif.device = wifi_radio
                wif.encryption = 'none'
                wif.ssid = vif.essid

                # We only allow automatic channel selection when all VIFs are in STA mode.
                if dsc_channel is None and vif.mode != 'sta':
                    raise cgm_base.ValidationError(_("Automatic channel selection is only allowed when all VIFs are in STA mode!"))

                if vif.mode == 'ap':
                    wif.mode = 'ap'

                    if vif.isolate_clients:
                        wif.isolate = True
                elif vif.mode == 'mesh':
                    wif.mode = 'adhoc'
                    wif.bssid = vif.bssid
                    # Override default mcast_rate to avoid broadcast traffic from
                    # stealing too much air time
                    wif.mcast_rate = 6000
                elif vif.mode == 'sta':
                    wif.mode = 'sta'

                    # Support automatic configuration from another AP node.
                    if vif.connect_to is not None:
                        target_interface = vif.get_target_interface()
                        if target_interface is None:
                            node_name = vif.connect_to.config.core.general().name
                            raise cgm_base.ValidationError(_("AP interface of node '%s' that this node is connecting to does not exist!") % node_name)

                        wif.ssid = target_interface.essid
                        if target_interface.device.ack_distance:
                            radio.distance = target_interface.device.ack_distance
                else:
                    raise cgm_base.ValidationError(_("Unsupported OpenWRT wireless interface mode '%s'!") % vif.mode)

                # Ensure that ESSID is not empty.
                if not wif.ssid:
                    raise cgm_base.ValidationError(_("ESSID of a wireless interface must not be empty!"))

                # Configure allowed bitrates.
                bitrates = []
                if vif.bitrates_preset is None:
                    # Allow all bitrates, no need to configure anything.
                    pass
                elif vif.bitrates_preset == 'exclude-80211b':
                    bitrates = dsc_protocol.get_rate_set(exclude=['802.11b'])
                elif vif.bitrates_preset == 'exclude-80211bg':
                    bitrates = dsc_protocol.get_rate_set(exclude=['802.11b', '802.11g'])
                elif vif.bitrates_preset == 'custom':
                    bitrates = [dsc_protocol.get_bitrate(x) for x in vif.bitrates]
                else:
                    raise cgm_base.ValidationError(_("Unsupported OpenWrt bitrate preset '%s'!") % vif.bitrates_preset)

                wif.basic_rate = []
                for bitrate in bitrates:
                    if bitrate.rate_set in ('802.11b', '802.11g'):
                        wif.basic_rate.append(int(bitrate.rate * 1000))
                    elif bitrate.rate_set in ('802.11n',):
                        # TODO: Configuring HT MCS rates is currently not supported.
                        pass
                    else:
                        raise cgm_base.ValidationError(_("Unsupported OpenWrt bitrate set '%s'!") % bitrate.rate_set)

                # Configure network interface for each vif, first being the primary network
                vif_name = device.get_vif_mapping(cfg.platform, interface.wifi_radio, vif)
                wif.ifname = vif_name

                bridge = check_interface_bridged(vif)
                if bridge is not None:
                    # Wireless interfaces are reverse-configured to be part of a bridge
                    wif.network = bridge.name
                else:
                    iface = cfg.network.add(interface=vif_name, managed_by=vif)
                    wif.network = vif_name

                    if vif.uplink and vif.mode != 'sta':
                            raise cgm_base.ValidationError(_("Wireless interface may only be an uplink when in station mode!"))

                    configure_interface(cfg, node, vif, iface, vif_name)

            # Include wireless tools package.
            cfg.packages.add('wireless-tools')


@cgm_base.register_platform_module('openwrt', 15)
def dns_base(node, cfg):
    """
    Configures DNS servers.
    """

    # DNS configuration is part of the DHCP config.
    dnsmasq = cfg.dhcp.add('dnsmasq')
    dnsmasq.domainneeded = False
    dnsmasq.boguspriv = False
    dnsmasq.localise_queries = True
    dnsmasq.rebind_protection = False
    dnsmasq.nonegcache = True
    dnsmasq.noresolv = True
    dnsmasq.authoritative = True
    dnsmasq.leasefile = '/tmp/dhcp.leases'


@cgm_base.register_platform_module('openwrt', 15)
def firewall(node, cfg):
    """
    Configures the firewall.
    """

    # Configure netfilter defaults.
    cfg.sysctl.set_variable('net.netfilter.nf_conntrack_acct', 1)
    cfg.sysctl.set_variable('net.netfilter.nf_conntrack_checksum', 0)
    cfg.sysctl.set_variable('net.netfilter.nf_conntrack_max', 16384)
    cfg.sysctl.set_variable('net.netfilter.nf_conntrack_tcp_timeout_established', 7440)
    cfg.sysctl.set_variable('net.netfilter.nf_conntrack_udp_timeout', 60)
    cfg.sysctl.set_variable('net.netfilter.nf_conntrack_udp_timeout_stream', 180)

    # Disable bridge firewalling by default.
    cfg.sysctl.set_variable('net.bridge.bridge-nf-call-arptables', 0)
    cfg.sysctl.set_variable('net.bridge.bridge-nf-call-ip6tables', 0)
    cfg.sysctl.set_variable('net.bridge.bridge-nf-call-iptables', 0)

    # Setup chain defaults.
    defaults = cfg.firewall.add('defaults')
    defaults.synflood_protect = True
    defaults.input = 'ACCEPT'
    defaults.output = 'ACCEPT'
    defaults.forward = 'REJECT'


@cgm_base.register_platform_module('openwrt', 11)
def time_synchronization(node, cfg):
    """
    Sets up defaults for time synchronization.
    """

    ntp = cfg.system.add(timeserver='ntp')
    ntp.enable_server = False
    ntp.server = [
        '0.openwrt.pool.ntp.org',
        '1.openwrt.pool.ntp.org',
        '2.openwrt.pool.ntp.org',
        '3.openwrt.pool.ntp.org',
    ]

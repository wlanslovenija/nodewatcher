from django.conf import settings
from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.allocation.ip import models as pool_models
from nodewatcher.core.registry import exceptions as registry_exceptions
from nodewatcher.core.generator.cgm import models as cgm_models, base as cgm_base, resources as cgm_resources, devices as cgm_devices
from nodewatcher.utils import posix_tz

from . import builder as openwrt_builder


class UCIFormat:
    """
    Available UCI export formats.
    """

    # UCI dump
    DUMP = 1
    # UCI in multiple files
    FILES = 2


class UCISection(object):
    """
    Represents a configuration section in UCI.
    """

    def __init__(self, key=None, typ=None):
        """
        Class constructor.
        """

        self.__dict__['_key'] = key
        self.__dict__['_typ'] = typ
        self.__dict__['_values'] = {}

    def __setattr__(self, name, value):
        """
        Sets a configuration attribute.
        """

        self._values[name] = value

    def __delattr__(self, name):
        """
        Deletes a configuration attribute.
        """

        del self._values[name]

    def __getattr__(self, name):
        """
        Returns a configuration attribute's value.
        """

        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)

        return self._values.get(name, None)

    def get_key(self):
        """
        Returns the section key.
        """

        return self._key

    def get_type(self):
        """
        Returns the section type name.
        """

        return self._typ

    def format_value(self, key, value, root, section, idx=None, fmt=UCIFormat.DUMP):
        """
        Formats a value so it is suitable for insertion into UCI.
        """

        if fmt == UCIFormat.DUMP:
            if isinstance(value, (list, tuple)):
                value = ' '.join(str(x) for x in value)
            elif isinstance(value, bool):
                value = int(value)
            else:
                value = str(value).strip().replace('\n', ' ')

            if self._typ is not None:
                return ['{0}.{1}.{2}={3}'.format(root, section, key, value)]
            else:
                return ['{0}.@{1}[{2}].{3}={4}'.format(root, section, idx, key, value)]
        elif fmt == UCIFormat.FILES:
            if isinstance(value, (list, tuple)):
                return ['\tlist %s \'%s\'' % (key, item) for item in value]
            elif isinstance(value, bool):
                return ['\toption %s \'%s\'' % (key, int(value))]
            else:
                return ['\toption %s \'%s\'' % (key, str(value).strip().replace('\n', ' '))]

        return str(value)

    def format(self, root, section, idx=None, fmt=UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """

        output = []

        # Output section header
        if self._typ is not None:
            # Named sections
            if fmt == UCIFormat.DUMP:
                output.append('{0}.{1}={2}'.format(root, section, self._typ))
            elif fmt == UCIFormat.FILES:
                output.append('config %s \'%s\'' % (self._typ, section))
        else:
            # Ordered sections
            if fmt == UCIFormat.DUMP:
                output.append('{0}.@{1}[{2}]={1}'.format(root, section, idx))
            elif fmt == UCIFormat.FILES:
                output.append('config %s' % section)

        # Output section values
        for key, value in self._values.iteritems():
            if key.startswith('_'):
                continue
            output += self.format_value(key, value, root, section, idx, fmt)

        # Output section footer
        if fmt == UCIFormat.FILES:
            output.append('')

        return output


class UCIRoot(object):
    """
    Represents an UCI configuration file with multiple named and ordered
    sections.
    """

    def __init__(self, root):
        """
        Class constructor.

        :param root: Root name
        """

        self._root = root
        self._named_sections = {}
        self._ordered_sections = {}

    def add(self, *args, **kwargs):
        """
        Creates a new UCI section. An ordered section should be specified by using
        a single argument and a named section by using a single keyword argument.

        :return: The newly created UCISection
        """

        if len(args) > 1 or len(kwargs) > 1 or len(args) == len(kwargs):
            raise ValueError

        if kwargs:
            # Adding a named section
            section_key = kwargs.values()[0]
            section = UCISection(key=section_key, typ=kwargs.keys()[0])

            # Check for duplicates to avoid screwing up existing lists and sections
            if section_key in self._named_sections:
                raise ValueError("UCI section '{0}' is already defined!".format(section_key))

            self._named_sections[section_key] = section
        else:
            # Adding an ordered section
            section = UCISection()
            self._ordered_sections.setdefault(args[0], []).append(section)

        return section

    def named_sections(self):
        """
        Returns an iterator over the named sections.
        """

        return self._named_sections.iteritems()

    def ordered_sections(self):
        """
        Returns an iterator over the ordered sections.
        """

        return self._ordered_sections.iteritems()

    def find_named_section(self, section_type, **query):
        """
        Searches for the first named section having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: Named section or None if not found
        """

        for name, section in self.named_sections():
            if section.get_type() != section_type:
                continue

            if all((getattr(section, a, None) == v for a, v in query.items())):
                return section

    def find_ordered_section(self, section_type, **query):
        """
        Searches for the first ordered section having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: Ordered section or None if not found
        """

        for section in self._ordered_sections.get(section_type, []):
            if all((getattr(section, a, None) == v for a, v in query.items())):
                return section

    def __iter__(self):
        return self.named_sections()

    def __contains__(self, section):
        return section in self._named_sections or section in self._ordered_sections

    def __getattr__(self, section):
        """
        Retrieves the wanted UCI section.
        """

        if section.startswith('__') and section.endswith('__'):
            raise AttributeError(section)

        try:
            return self._named_sections[section]
        except KeyError:
            try:
                return self._ordered_sections[section]
            except KeyError:
                raise AttributeError(section)

    def format(self, fmt=UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.

        :param fmt: Wanted export format
        """

        output = []
        for name, section in self._named_sections.iteritems():
            output += section.format(self._root, name, fmt=fmt)

        for name, sections in self._ordered_sections.iteritems():
            for idx, section in enumerate(sections):
                output += section.format(self._root, name, idx, fmt=fmt)

        return output


class UCIConfiguration(cgm_base.PlatformConfiguration):
    """
    An in-memory implementation of UCI configuration.
    """

    def __init__(self):
        """
        Class constructor.
        """
        super(UCIConfiguration, self).__init__()
        self._roots = {}

    def get_build_config(self):
        """
        Returns a build configuration which must be JSON-serializable. This
        configuration will be passed to the backend builder function and must
        contain anything that the builder will need to configure the generated
        firmware.
        """

        result = self.format(fmt=UCIFormat.FILES)
        result.update(super(UCIConfiguration, self).get_build_config())
        return result

    def __getattr__(self, root):
        """
        Returns the desired UCI root (config file).
        """

        if root.startswith('__') and root.endswith('__'):
            raise AttributeError(root)

        return self._roots.setdefault(root, UCIRoot(root))

    def format(self, fmt=UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.

        :param fmt: Wanted export format
        """

        if fmt == UCIFormat.DUMP:
            # UCI dump format
            output = []
            for name, root in self._roots.iteritems():
                output += root.format(fmt=fmt)
        elif fmt == UCIFormat.FILES:
            # UCI split into multiple files
            output = {}
            for name, root in self._roots.iteritems():
                output[name] = '\n'.join(root.format(fmt=fmt))

        return output


class PlatformOpenWRT(cgm_base.PlatformBase):
    """
    OpenWRT platform descriptor.
    """

    config_class = UCIConfiguration

    def build(self, result):
        """
        Builds the firmware using a previously generated and properly
        formatted configuration.

        :param result: Destination build result
        :return: A list of generated firmware files
        """

        # Extract the device descriptor to get the profile
        device = result.node.config.core.general().get_device()
        profile = device.profiles['openwrt']

        return openwrt_builder.build_image(result, profile)

cgm_base.register_platform('openwrt', _("OpenWRT"), PlatformOpenWRT())


@cgm_base.register_platform_module('openwrt', 10)
def general(node, cfg):
    """
    General configuration for nodewatcher firmware.
    """

    system = cfg.system.add('system')
    system.hostname = node.config.core.general().name
    system.uuid = node.uuid

    try:
        zone = node.config.core.location().timezone.zone
        system.timezone = posix_tz.get_posix_tz(zone)
        if not system.timezone:
            raise cgm_base.ValidationError(_("Unsupported OpenWRT timezone '%s'!") % zone)
    except (registry_exceptions.RegistryItemNotRegistered, AttributeError):
        system.timezone = posix_tz.get_posix_tz(settings.TIME_ZONE)
        if not system.timezone:
            system.timezone = 'UTC'

    # Setup base packages to be installed
    # TODO: This should probably not be hardcoded (or at least moved to modules)
    cfg.packages.update([
        'nodewatcher-watchdog'
    ])


@cgm_base.register_platform_module('openwrt', 1)
def router_id(node, cfg):
    """
    Registers all router identifiers for use by routing CGMs.
    """

    for rid in node.config.core.routerid():
        if isinstance(rid, core_models.StaticIpRouterIdConfig):
            res = cgm_resources.IpResource(rid.rid_family, rid.address, rid)
            cfg.resources.add(res)
        elif isinstance(rid, pool_models.AllocatedIpRouterIdConfig):
            # Check that the network has actually been allocated and fail validation if not so
            if not rid.allocation:
                raise cgm_base.ValidationError(_("Missing network allocation in router ID configuration."))

            res = cgm_resources.IpResource(rid.family, rid.allocation.ip_subnet, rid)
            cfg.resources.add(res)


@cgm_base.register_platform_module('openwrt', 11)
def user_accounts(node, cfg):
    """
    Configures password authentication for root user account.
    """

    cfg.accounts.add_user('nobody', '*', 65534, 65534, '/var', '/bin/false')

    try:
        auth = node.config.core.authentication(onlyclass=cgm_models.PasswordAuthenticationConfig).get()
        cfg.accounts.add_user('root', auth.password, 0, 0, '/tmp', '/bin/ash')
    except cgm_models.AuthenticationConfig.MultipleObjectsReturned:
        raise cgm_base.ValidationError(_("Multiple root passwords are not supported!"))
    except cgm_models.AuthenticationConfig.DoesNotExist:
        pass


def configure_leasable_network(cfg, network, iface_name, subnet):
    """
    A helper function to configure network lease.

    :param cfg: Platform configuration
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


def configure_network(cfg, network, section, iface_name):
    """
    A helper function to configure an interface's network.

    :param cfg: Platform configuration
    :param network: Network configuration
    :param section: UCI interface or alias section
    :param iface_name: Name of the UCI interface
    """

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

        # When network is marked to be announced, also specify it here
        section._announce = network.routing_announces

        configure_leasable_network(cfg, network, iface_name, network.address)
    elif isinstance(network, cgm_models.AllocatedNetworkConfig):
        section.proto = 'static'

        # When network is marked to be announced, also specify it here
        section._announce = network.routing_announces

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

            configure_leasable_network(cfg, network, iface_name, address)
        else:
            raise cgm_base.ValidationError(_("Unsupported address family '%s'!") % network.family)
    elif isinstance(network, cgm_models.DHCPNetworkConfig):
        section.proto = 'dhcp'
        section.hostname = cfg.system.system[0].hostname
    elif isinstance(network, cgm_models.PPPoENetworkConfig):
        section.proto = 'pppoe'
        section.username = network.username
        section.password = network.password

        # Package 'ppp-mod-pppoe' is required for using PPPoE
        cfg.packages.update(['ppp-mod-pppoe'])
    else:
        section.proto = 'none'


def configure_interface(cfg, interface, section, iface_name):
    """
    A helper function to configure an interface.

    :param cfg: Platform configuration
    :param interface: Interface configuration
    :param section: UCI interface section
    :param iface_name: Name of the UCI interface
    """

    section._routable = getattr(interface, 'routing_protocols', [])

    networks = [x.cast() for x in interface.networks.all()]
    if networks:
        network = networks[0]
        configure_network(cfg, network, section, iface_name)

        # Additional network configurations are aliases
        for network in networks[1:]:
            alias = cfg.network.add('alias')
            alias.interface = iface_name
            configure_network(cfg, network, alias, iface_name)
    else:
        section.proto = 'none'

    # Configure QoS for this interface when specified
    for limit in interface.limits.filter(enabled=True):
        limit = limit.cast()
        if not isinstance(limit, cgm_models.ThroughputInterfaceLimitConfig):
            # We currently only support bandwidth limits
            continue

        qos = cfg.qos.add(interface=iface_name)
        qos.enabled = True
        qos.classgroup = 'Default'

        if limit.limit_in:
            qos.download = limit.limit_in
        if limit.limit_out:
            qos.upload = limit.limit_out

        # Only take the first bandwidth limit into account and ignore the rest
        break

    # Configure firewall policy for this interface
    if section._uplink:
        firewall = cfg.firewall.find_ordered_section('zone', name='uplink')
        if not firewall:
            firewall = cfg.firewall.add('zone')
            firewall.name = 'uplink'
            firewall.input = 'ACCEPT'
            firewall.output = 'ACCEPT'
            firewall.forward = 'REJECT'

        if not firewall.network:
            firewall.network = []

        firewall.network.append(iface_name)


def configure_switch(cfg, device, port):
    """
    Configures a switch port.

    :param cfg: Platform configuration
    :param device: Device descriptor
    :param port: Port descriptor
    """

    switch = device.get_switch(port.switch)
    switch_iface = device.remap_port('openwrt', port.switch)

    # Enable switch if not yet enabled
    try:
        sw = cfg.network.add(switch=switch_iface)
        sw.enable_vlan = True
    except ValueError:
        # Switch is already enabled
        pass

    # Check if wanted VLAN is already configured
    if 'switch_vlan' in cfg.network:
        for vlan in cfg.network.switch_vlan:
            if vlan.vlan == port.vlan:
                raise cgm_base.ValidationError(_("VLAN assignment conflict while trying to configure switch!"))

    # Configure VLAN
    vlan = cfg.network.add('switch_vlan')
    vlan.device = switch_iface
    vlan.vlan = port.vlan
    ports = []
    for p in port.ports:
        if p in switch.cpu_ports and switch.cpu_tagged:
            p = '%st' % p
        ports.append(str(p))
    vlan.ports = ' '.join(ports)


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

    # Configure default routing table names
    cfg.routing_tables.set_table('local', 255)
    cfg.routing_tables.set_table('main', 254)
    cfg.routing_tables.set_table('default', 253)
    cfg.routing_tables.set_table('unspec', 0)

    # Obtain the device descriptor for this device
    device = node.config.core.general().get_device()

    # Configure all interfaces
    for interface in node.config.core.interfaces():
        if not interface.enabled:
            continue

        if isinstance(interface, cgm_models.BridgeInterfaceConfig):
            iface_name = device.get_bridge_mapping('openwrt', interface)
            iface = cfg.network.add(interface=iface_name)
            iface.type = 'bridge'

            # Configure bridge interfaces
            iface.ifname = []
            for port in interface.bridge_ports.all():
                port = port.interface
                if isinstance(port, cgm_models.EthernetInterfaceConfig):
                    raw_port = device.remap_port('openwrt', port.eth_port)
                    if isinstance(raw_port, (list, tuple)):
                        iface.ifname += raw_port
                    else:
                        iface.ifname.append(raw_port)

                    if port.uplink:
                        iface._uplink = True
                        set_dhcp_ignore(cfg, iface_name)

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

            configure_interface(cfg, interface, iface, iface_name)
        elif isinstance(interface, cgm_models.MobileInterfaceConfig):
            iface = cfg.network.add(interface=interface.device)
            iface._uplink = True
            set_dhcp_ignore(cfg, interface.device)

            # Mapping of device identifiers to ports
            port_map = {
                'mobile0': '/dev/ttyUSB0',
                'mobile1': '/dev/ttyUSB1',
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
            iface.pincode = interface.pin
            if interface.username:
                iface.username = interface.username
                iface.password = interface.password

            configure_interface(cfg, interface, iface, interface.device)
            iface.proto = '3g'

            # Some packages are required for using a mobile interface
            cfg.packages.update([
                'comgt',
                'usb-modeswitch',
                'kmod-usb-serial',
                'kmod-usb-serial-option',
                'kmod-usb-serial-wwan',
                'kmod-usb-ohci',
                'kmod-usb-uhci',
                'kmod-usb-acm',
                'kmod-usb2',
            ])
        elif isinstance(interface, cgm_models.EthernetInterfaceConfig):
            if check_interface_bridged(interface) is not None:
                continue

            try:
                iface = cfg.network.add(interface=interface.eth_port)
            except ValueError:
                raise cgm_base.ValidationError(
                    _("Duplicate interface definition for port '%s'!") % interface.eth_port
                )

            iface.ifname = device.remap_port('openwrt', interface.eth_port)
            if iface.ifname is None:
                raise cgm_base.ValidationError(
                    _("No port remapping for port '%(port)s' of device '%s(device_name)' is available!") % {'port': interface.eth_port, 'device_name': device.name}
                )

            if isinstance(iface.ifname, (list, tuple)):
                iface.type = 'bridge'

            if interface.uplink:
                iface._uplink = True
                set_dhcp_ignore(cfg, interface.eth_port)

            if interface.mac_address:
                iface.macaddr = interface.mac_address

            configure_interface(cfg, interface, iface, interface.eth_port)

            # Check if we need to configure the switch
            port = device.get_port(interface.eth_port)
            if isinstance(port, cgm_devices.SwitchedEthernetPort):
                configure_switch(cfg, device, port)
        elif isinstance(interface, cgm_models.WifiRadioDeviceConfig):
            # Configure virtual interfaces on top of the same radio device
            dsc_radio = device.get_radio(interface.wifi_radio)
            interfaces = list(interface.interfaces.all())
            if len(interfaces) > 1 and not dsc_radio.has_feature(cgm_devices.DeviceRadio.MultipleSSID):
                raise cgm_base.ValidationError(_("Router '%s' does not support multiple SSIDs!") % device.name)

            wifi_radio = device.remap_port('openwrt', interface.wifi_radio)
            try:
                radio = cfg.wireless.add(**{'wifi-device': wifi_radio})
            except ValueError:
                raise cgm_base.ValidationError(
                    _("Duplicate radio definition for radio '%s'!") % interface.wifi_radio
                )

            try:
                radio.type = device.drivers['openwrt'][interface.wifi_radio]
            except KeyError:
                raise cgm_base.ValidationError(
                    _("Radio driver for '%s' not defined on OpenWRT!") % interface.wifi_radio
                )

            dsc_protocol = dsc_radio.get_protocol(interface.protocol)
            dsc_channel = dsc_protocol.get_channel(interface.channel) if interface.channel else None
            dsc_channel_width = dsc_protocol.get_channel_width(interface.channel_width)

            # Select proper hardware mode
            if dsc_protocol.identifier in ('ieee-80211bg', 'ieee-80211bgn'):
                radio.hwmode = '11g'
            elif dsc_protocol.identifier in ('ieee-80211a', 'ieee-80211an'):
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
                    radio.chanbw = 20
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
                        if target_interface.ack_distance:
                            radio.distance = target_interface.ack_distance
                else:
                    raise cgm_base.ValidationError(_("Unsupported OpenWRT wireless interface mode '%s'!") % vif.mode)

                # Ensure that ESSID is not empty.
                if not wif.ssid:
                    raise cgm_base.ValidationError(_("ESSID of a wireless interface must not be empty!"))

                # Configure network interface for each vif, first being the primary network
                vif_name = device.get_vif_mapping('openwrt', interface.wifi_radio, vif)
                wif.ifname = vif_name

                bridge = check_interface_bridged(vif)
                if bridge is not None:
                    # Wireless interfaces are reverse-configured to be part of a bridge
                    wif.network = bridge.name
                else:
                    iface = cfg.network.add(interface=vif_name)
                    wif.network = vif_name
                    configure_interface(cfg, vif, iface, vif_name)


@cgm_base.register_platform_module('openwrt', 15)
def qos_base(node, cfg):
    """
    Configures basic QoS rules (independent of interfaces).
    """

    def add_classify(target, ports, proto=None):
        c = cfg.qos.add('classify')
        c.target = target
        c.ports = ','.join([str(x) for x in ports])
        if proto is not None:
            c.proto = proto

    def add_default(target, proto=None, portrange=None, pktsize=None):
        d = cfg.qos.add('default')
        d.target = target
        if proto is not None:
            d.proto = proto
        if portrange is not None:
            d.portrange = '%d-%d' % portrange
        if pktsize is not None:
            d.pktsize = pktsize

    def add_reclassify(target, proto=None, pktsize=None, mark=None, tcpflags=None):
        r = cfg.qos.add('reclassify')
        r.target = target
        if proto is not None:
            r.proto = proto
        if pktsize is not None:
            r.pktsize = pktsize
        if mark is not None:
            r.mark = mark
        if tcpflags is not None:
            r.tcpflags = tcpflags

    def add_classgroup(name, classes, default):
        g = cfg.qos.add(classgroup=name)
        g.classes = ' '.join(classes)
        g.default = default

    def add_class(name, packetsize=None, packetdelay=None, maxsize=None, avgrate=None, priority=None):
        c = cfg.qos.add(**{'class': name})
        if packetsize is not None:
            c.packetsize = packetsize
        if packetdelay is not None:
            c.packetdelay = packetdelay
        if maxsize is not None:
            c.maxsize = maxsize
        if avgrate is not None:
            c.avgrate = avgrate
        if priority is not None:
            c.priority = priority

    # Configure default OpenWrt QoS rules
    add_classify(target='Priority', ports=[22, 53])
    add_classify(target='Normal', proto='tcp', ports=[20, 21, 25, 80, 110, 443, 993, 995])
    add_classify(target='Express', ports=[5190])
    add_default(target='Express', proto='udp', pktsize=-500)
    add_reclassify(target='Priority', proto='icmp')
    add_default(target='Bulk', portrange=(1024, 65535))
    add_reclassify(target='Priority', proto='tcp', pktsize=-128, mark='!Bulk', tcpflags='SYN')
    add_reclassify(target='Priority', proto='tcp', pktsize=-128, mark='!Bulk', tcpflags='ACK')
    add_classgroup(name='Default', classes=['Priority', 'Express', 'Normal', 'Bulk'], default='Normal')
    add_class(name='Priority', packetsize=400, maxsize=400, avgrate=10, priority=20)
    add_class(name='Priority_down', packetsize=1000, avgrate=10)
    add_class(name='Express', packetsize=1000, maxsize=800, avgrate=50, priority=10)
    add_class(name='Normal', packetsize=1500, packetdelay=100, avgrate=10, priority=5)
    add_class(name='Normal_down', avgrate=20)
    add_class(name='Bulk', avgrate=1, packetdelay=200)

    # Ensure that we have qos-scripts installed
    cfg.packages.update(['qos-scripts'])


@cgm_base.register_platform_module('openwrt', 15)
def dns_servers(node, cfg):
    """
    Configures DNS servers.
    """

    # DNS configuration is part of the DHCP config
    dnsmasq = cfg.dhcp.add('dnsmasq')
    dnsmasq.domainneeded = False
    dnsmasq.boguspriv = False
    dnsmasq.localise_queries = True
    dnsmasq.rebind_protection = False
    dnsmasq.nonegcache = True
    dnsmasq.noresolv = True
    dnsmasq.authoritative = True
    dnsmasq.leasefile = '/tmp/dhcp.leases'
    dnsmasq.server = [str(x.address.ip) for x in node.config.core.servers.dns()]


@cgm_base.register_platform_module('openwrt', 15)
def firewall(node, cfg):
    """
    Configures the firewall.
    """

    # Setup chain defaults
    defaults = cfg.firewall.add('defaults')
    defaults.synflood_protect = True
    defaults.input = 'ACCEPT'
    defaults.output = 'ACCEPT'
    defaults.forward = 'REJECT'

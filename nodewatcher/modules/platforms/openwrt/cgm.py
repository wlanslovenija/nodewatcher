from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import models as cgm_models, base as cgm_base, resources as cgm_resources, routers as cgm_routers
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
    def __init__(self, typ = None):
        """
        Class constructor.
        """
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

    def get_type(self):
        """
        Returns the section type name.
        """
        return self._typ

    def format_value(self, key, value, root, section, idx = None, fmt = UCIFormat.DUMP):
        """
        Formats a value so it is suitable for insertion into UCI.
        """

        if fmt == UCIFormat.DUMP:
            if isinstance(value, (list, tuple)):
                value = " ".join(str(x) for x in value)
            elif isinstance(value, bool):
                value = int(value)
            else:
                value = str(value)

            if self._typ is not None:
                return ["{0}.{1}.{2}={3}".format(root, section, key, value)]
            else:
                return ["{0}.@{1}[{2}].{3}={4}".format(root, section, idx, key, value)]
        elif fmt == UCIFormat.FILES:
            if isinstance(value, (list, tuple)):
                return ['\tlist %s \'%s\'' % (key, item) for item in value]
            elif isinstance(value, bool):
                return ['\toption %s \'%s\'' % (key, int(value))]
            else:
                return ['\toption %s \'%s\'' % (key, value)]

        return str(value)

    def format(self, root, section, idx = None, fmt = UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """
        output = []

        
        # Output section header
        if self._typ is not None:
            # Named sections
            if fmt == UCIFormat.DUMP:
                output.append("{0}.{1}={2}".format(root, section, self._typ))
            elif fmt == UCIFormat.FILES:
                output.append('config %s \'%s\'' % (self._typ, section))
        else:
            # Ordered sections
            if fmt == UCIFormat.DUMP:
                output.append("{0}.@{1}[{2}]={1}".format(root, section, idx))
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
            section = UCISection(typ = kwargs.keys()[0])

            # Check for duplicates to avoid screwing up existing lists and sections
            if section_key in self._named_sections:
                raise ValueError, "UCI section '{0}' is already defined!".format(section_key)

            self._named_sections[section_key] = section
        else:
            # Adding an ordered section
            section = UCISection()
            self._ordered_sections.setdefault(args[0], []).append(section)

        return section

    def __iter__(self):
        return iter(self._named_sections.iteritems())

    def __contains__(self, section):
        return section in self._named_sections or  section in self._ordered_sections

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

    def format(self, fmt = UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.

        :param fmt: Wanted export format
        """

        output = []
        for name, section in self._named_sections.iteritems():
            output += section.format(self._root, name, fmt = fmt)

        for name, sections in self._ordered_sections.iteritems():
            for idx, section in enumerate(sections):
                output += section.format(self._root, name, idx, fmt = fmt)

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

    def __getattr__(self, root):
        """
        Returns the desired UCI root (config file).
        """

        if root.startswith('__') and root.endswith('__'):
            raise AttributeError(root)

        return self._roots.setdefault(root, UCIRoot(root))

    def format(self, fmt = UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.

        :param fmt: Wanted export format
        """

        if fmt == UCIFormat.DUMP:
            # UCI dump format
            output = []
            for name, root in self._roots.iteritems():
                output += root.format(fmt = fmt)
        elif fmt == UCIFormat.FILES:
            # UCI split into multiple files
            output = {}
            for name, root in self._roots.iteritems():
                output[name] = "\n".join(root.format(fmt = fmt))

        return output

class PlatformOpenWRT(cgm_base.PlatformBase):
    """
    OpenWRT platform descriptor.
    """
    config_class = UCIConfiguration

    def build(self, node, cfg):
        """
        Builds the firmware using a previously generated and properly
        formatted configuration.

        :param node: Node instance to build the firmware for
        :param cfg: Generated configuration (platform-dependent)
        :return: A list of generated firmware files
        """
        # Extract the router descriptor to get architecture and profile
        router = node.config.core.general().get_device()
        profile = router.profiles['openwrt']

        # Format UCI configuration and start the build process
        formatted_cfg = cfg.format(fmt = UCIFormat.FILES)
        return openwrt_builder.build_image(formatted_cfg, router.architecture, profile, cfg.packages)

cgm_base.register_platform("openwrt", _("OpenWRT"), PlatformOpenWRT())

# Load supported routers
from . import fon, linksys, buffalo, mikrotik, asus, tplink, ubnt

@cgm_base.register_platform_module("openwrt", 10)
def general(node, cfg):
    """
    General configuration for nodewatcher firmware.
    """
    system = cfg.system.add("system")
    system.hostname = node.config.core.general().name
    system.uuid = node.uuid
    # TODO: Timezone should probably not be hardcoded
    system.timezone = "CET-1CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00"

    # Setup base packages to be installed
    # TODO: This should probably not be hardcoded (or at least moved to modules)
    cfg.packages.update(["nodewatcher-core", "nodewatcher-watchdog"])

def configure_network(cfg, network, section):
    """
    A helper function to configure an interface's network.

    :param cfg: Platform configuration
    :param network: Network configuration
    :param section: UCI interface or alias section
    """
    if isinstance(network, cgm_models.StaticNetworkConfig):
        section.proto = "static"
        if network.family == "ipv4":
            section.ipaddr = network.address.ip
            section.netmask = network.address.netmask
            section.gateway = network.gateway.ip
        elif network.family == "ipv6":
            section.ip6addr = network.address
            section.ip6gw = network.gateway.ip
        else:
            raise cgm_base.ValidationError(_("Unsupported address family '%s'!") % network.family)
    elif isinstance(network, cgm_models.AllocatedNetworkConfig):
        section.proto = "static"

        # When network is marked to be announced, also specify it here
        if network.routing_announce:
            section._announce = [network.routing_announce]

        if network.family in ("ipv4", "ipv6"):
            # Make our subnet available to other modules as a resource
            res = cgm_resources.IpResource(network.family, network.allocation.ip_subnet, network)
            cfg.resources.add(res)
            address = res.allocate()

            if network.family == "ipv4":
                section.ipaddr = address.ip
                section.netmask = address.netmask
            elif network.family == "ipv6":
                section.ip6addr = address
        else:
            raise cgm_base.ValidationError(_("Unsupported address family '%s'!") % network.family)
    elif isinstance(network, cgm_models.DHCPNetworkConfig):
        section.proto = "dhcp"
    else:
        section.proto = "none"

def configure_interface(cfg, interface, section, iface_name):
    """
    A helper function to configure an interface.

    :param cfg: Platform configuration
    :param interface: Interface configuration
    :param section: UCI interface section
    :param iface_name: Name of the UCI interface
    """
    section._routable = interface.routing_protocol

    networks = [x.cast() for x in interface.networks.all()]
    if networks:
        network = networks[0]
        configure_network(cfg, network, section)

        # Additional network configurations are aliases
        for network in networks[1:]:
            alias = cfg.network.add("alias")
            alias.interface = iface_name
            configure_network(cfg, network, alias)
    else:
        section.proto = "none"

    # Configure QoS for this interface when specified
    for limit in interface.limits.filter(enabled = True):
        limit = limit.cast()
        if not isinstance(limit, cgm_models.ThroughputInterfaceLimitConfig):
            # We currently only support bandwidth limits
            continue

        qos = cfg.qos.add(interface = iface_name)
        qos.enabled = True
        qos.classgroup = 'Default'

        if limit.limit_in:
            qos.download = limit.limit_in
        if limit.limit_out:
            qos.upload = limit.limit_out

        # Only take the first bandwidth limit into account and ignore the rest
        break

def configure_switch(cfg, router, port):
    """
    Configures a switch port.

    :param cfg: Platform configuration
    :param router: Router descriptor
    :param port: Port descriptor
    """
    switch = router.get_switch(port.switch)
    switch_iface = router.remap_port("openwrt", port.switch)

    # Enable switch if not yet enabled
    try:
        sw = cfg.network.add(switch = switch_iface)
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
    vlan = cfg.network.add("switch_vlan")
    vlan.device = switch_iface
    vlan.vlan = port.vlan
    vlan.ports = " ".join([str(x) for x in port.ports])

@cgm_base.register_platform_module("openwrt", 10)
def network(node, cfg):
    """
    Basic network configuration.
    """
    lo = cfg.network.add(interface = "loopback")
    lo.ifname = "lo"
    lo.proto = "static"
    lo.ipaddr = "127.0.0.1"
    lo.netmask = "255.0.0.0"

    # Obtain the router descriptor for this device
    router = node.config.core.general().get_device()

    # Configure all interfaces
    for interface in node.config.core.interfaces():
        if not interface.enabled:
            continue

        if isinstance(interface, cgm_models.EthernetInterfaceConfig):
            try:
                iface = cfg.network.add(interface = interface.eth_port)
            except ValueError:
                raise cgm_base.ValidationError(_("Duplicate interface definition for port '%s'!") %
                                               interface.eth_port)

            iface.ifname = router.remap_port("openwrt", interface.eth_port)
            if iface.ifname is None:
                raise cgm_base.ValidationError(_("No port remapping for port '%s' of router '%s' is available!") %\
                                               (interface.eth_port, router.name))

            if interface.uplink:
                iface._uplink = True

            configure_interface(cfg, interface, iface, interface.eth_port)

            # Check if we need to configure the switch
            port = router.get_port(interface.eth_port)
            if isinstance(port, cgm_routers.SwitchedEthernetPort):
                configure_switch(cfg, router, port)
        elif isinstance(interface, cgm_models.WifiRadioDeviceConfig):
            # Configure virtual interfaces on top of the same radio device
            interfaces = list(interface.interfaces.all())
            if len(interfaces) > 1 and cgm_routers.Features.MultipleSSID not in router.features:
                raise cgm_base.ValidationError(_("Router '%s' does not support multiple SSIDs!") % router.name)

            wifi_radio = router.remap_port("openwrt", interface.wifi_radio)
            try:
                radio = cfg.wireless.add(**{ "wifi-device" : wifi_radio })
            except ValueError:
                raise cgm_base.ValidationError(_("Duplicate radio definition for radio '%s'!") %
                                               interface.wifi_radio)

            dsc_radio = router.get_radio(interface.wifi_radio)
            dsc_protocol = dsc_radio.get_protocol(interface.protocol)
            dsc_channel = dsc_protocol.get_channel(interface.channel)
            if dsc_protocol.identifier == "ieee-80211bg":
                radio.hwmode = '11g'
            elif dsc_protocol.identifier == "ieee-80211n":
                radio.hwmode = '11ng'
                radio.htmode = 'HT20' # TODO: Should band width be made configurable?
                radio.ht_capab = []

                for capability in dsc_protocol.available_capabilities:
                    radio.ht_capab.append(capability.identifier)
            else:
                raise cgm_base.ValidationError(_("Unsupported OpenWRT wireless protocol '%s'!") % dsc_protocol.identifier)

            radio.phy = "phy%d" % dsc_radio.index
            radio.channel = dsc_channel.number

            for index, vif in enumerate(interfaces):
                wif = cfg.wireless.add("wifi-iface")
                wif.device = wifi_radio
                wif.encryption = "none"
                wif.ssid = vif.essid

                if vif.mode == "ap":
                    wif.mode = "ap"
                elif vif.mode == "mesh":
                    wif.mode = "adhoc"
                    wif.bssid = vif.bssid
                else:
                    raise cgm_base.ValidationError(_("Unsupported OpenWRT wireless interface mode '%s'!") % vif.mode)

                # Configure network interface for each vif, first being the primary network
                vif_name = "%sv%d" % (wifi_radio, index)
                iface = cfg.network.add(interface = vif_name)
                wif.network = vif_name

                configure_interface(cfg, vif, iface, vif_name)

@cgm_base.register_platform_module("openwrt", 10)
def qos_base(node, cfg):
    """
    Configures basic QoS rules (independent of interfaces).
    """
    def add_classify(target, ports, proto = None):
        c = cfg.qos.add("classify")
        c.target = target
        c.ports = ",".join([str(x) for x in ports])
        if proto is not None:
            c.proto = proto

    def add_default(target, proto = None, portrange = None, pktsize = None):
        d = cfg.qos.add("default")
        d.target = target
        if proto is not None:
            d.proto = proto
        if portrange is not None:
            d.portrange = "%d-%d" % portrange
        if pktsize is not None:
            d.pktsize = pktsize

    def add_reclassify(target, proto = None, pktsize = None, mark = None, tcpflags = None):
        r = cfg.qos.add("reclassify")
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
        g = cfg.qos.add(classgroup = name)
        g.classes = " ".join(classes)
        g.default = default

    def add_class(name, packetsize = None, packetdelay = None, maxsize = None, avgrate = None, priority = None):
        c = cfg.qos.add(**{ 'class' : name })
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
    add_classify(target = 'Priority', ports = [22, 53])
    add_classify(target = 'Normal', proto = 'tcp', ports = [20, 21, 25, 80, 110, 443, 993, 995])
    add_classify(target = 'Express', ports = [5190])
    add_default(target = 'Express', proto = 'udp', pktsize = -500)
    add_reclassify(target = 'Priority', proto = 'icmp')
    add_default(target = 'Bulk', portrange = (1024, 65535))
    add_reclassify(target = 'Priority', proto = 'tcp', pktsize = -128, mark = '!Bulk', tcpflags = 'SYN')
    add_reclassify(target = 'Priority', proto = 'tcp', pktsize = -128, mark = '!Bulk', tcpflags = 'ACK')
    add_classgroup(name = 'Default', classes = ['Priority', 'Express', 'Normal', 'Bulk'], default = 'Normal')
    add_class(name = 'Priority', packetsize = 400, maxsize = 400, avgrate = 10, priority = 20)
    add_class(name = 'Priority_down', packetsize = 1000, avgrate = 10)
    add_class(name = 'Express', packetsize = 1000, maxsize = 800, avgrate = 50, priority = 10)
    add_class(name = 'Normal', packetsize = 1500, packetdelay = 100, avgrate = 10, priority = 5)
    add_class(name = 'Normal_down', avgrate = 20)
    add_class(name = 'Bulk', avgrate = 1, packetdelay = 200)
    
    # Ensure that we have qos-scripts installed
    cfg.packages.update(["qos-scripts"])

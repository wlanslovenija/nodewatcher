from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import models as cgm_models, base as cgm_base, resources as cgm_resources, routers as cgm_routers

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
        return self._values.get(name, None)

    def get_type(self):
        """
        Returns the section type name.
        """
        return self._typ

    def format_value(self, value):
        """
        Formats a value so it is suitable for insertion into UCI.
        """
        if isinstance(value, (list, tuple)):
            return " ".join(self.format_value(x) for x in value)
        elif isinstance(value, bool):
            return int(value)

        return str(value)

    def format(self, root, section, idx = None):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """
        output = []

        if self._typ is not None:
            # Named sections
            output.append("{0}.{1}={2}".format(root, section, self._typ))
            for key, value in self._values.iteritems():
                if key.startswith('_'):
                    continue
                output.append("{0}.{1}.{2}={3}".format(root, section, key, self.format_value(value)))
        else:
            # Ordered sections
            output.append("{0}.@{1}[{2}]={1}".format(root, section, idx))
            for key, value in self._values.iteritems():
                if key.startswith('_'):
                    continue
                output.append("{0}.@{1}[{2}].{3}={4}".format(root, section, idx, key, self.format_value(value)))

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
        try:
            return self._named_sections[section]
        except KeyError:
            return self._ordered_sections[section]

    def format(self):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """
        output = []
        for name, section in self._named_sections.iteritems():
            output += section.format(self._root, name)

        for name, sections in self._ordered_sections.iteritems():
            for idx, section in enumerate(sections):
                output += section.format(self._root, name, idx)

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
        return self._roots.setdefault(root, UCIRoot(root))

    def format(self):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """
        output = []
        for name, root in self._roots.iteritems():
            output += root.format()

        return output

class PlatformOpenWRT(cgm_base.PlatformBase):
    """
    OpenWRT platform descriptor.
    """
    config_class = UCIConfiguration

    def format(self, cfg):
        """
        Formats the concrete configuration so that it is suitable for
        inclusion directly into the firmware image.

        :param cfg: Generated configuration (platform-dependent)
        :return: Platform-dependent object
        """
        # TODO: Split UCI configuration into files, return a dictionary containing a mapping from file names to their contents
        raise NotImplementedError

    def build(self, formatted_cfg):
        """
        Builds the firmware using a previously generated and properly
        formatted configuration.

        :param formatted_cfg: Formatted configuration (platform-dependent)
        :return: Build process result
        """
        # TODO: Setup the image builder fraemwork, write the formatted configuration to the filesystem, use the proper builder profile and build the firmware

        # TODO: How to define build profile? Modules should probably specify that somehow (a special UCI configuration package called "build"?)
        raise NotImplementedError

cgm_base.register_platform("openwrt", _("OpenWRT"), PlatformOpenWRT())

# Load supported routers
from . import fon, linksys, buffalo, mikrotik, asus, tplink

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
            iface = cfg.network.add(interface = interface.eth_port)
            iface.ifname = router.remap_port("openwrt", interface.eth_port)
            if iface.ifname is None:
                raise cgm_base.ValidationError(_("No port remapping for port '%s' of router '%s' is available!") %\
                                               (interface.eth_port, router.name))

            if interface.uplink:
                iface._uplink = True

            configure_interface(cfg, interface, iface, interface.eth_port)
        elif isinstance(interface, cgm_models.WifiRadioDeviceConfig):
            # Configure virtual interfaces on top of the same radio device
            interfaces = list(interface.interfaces.all())
            if len(interfaces) > 1 and cgm_routers.Features.MultipleSSID not in router.features:
                raise cgm_base.ValidationError(_("Router '%s' does not support multiple SSIDs!") % router.name)

            wifi_radio = router.remap_port("openwrt", interface.wifi_radio)
            radio = cfg.wireless.add(**{ "wifi-device" : wifi_radio })

            dsc_radio = router.get_radio(interface.wifi_radio)
            dsc_protocol = dsc_radio.get_protocol(interface.protocol)
            dsc_channel = dsc_protocol.get_channel(interface.channel)
            # TODO protocol details
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

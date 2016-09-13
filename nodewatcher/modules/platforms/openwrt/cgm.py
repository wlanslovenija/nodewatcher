import collections
import re

from django.conf import settings
from django.utils import crypto
from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.allocation.ip import models as pool_models
from nodewatcher.core.registry import exceptions as registry_exceptions
from nodewatcher.core.generator.cgm import models as cgm_models, base as cgm_base, resources as cgm_resources, devices as cgm_devices
from nodewatcher.utils import posix_tz

from . import builder as openwrt_builder

# Support different versions of libapt bindings.
try:
    import apt_pkg
    apt_pkg.init()
    apt_version_compare = apt_pkg.version_compare
except ImportError:
    try:
        import apt
        apt_version_compare = apt.VersionCompare
    except (ImportError, AttributeError):
        apt_version_compare = None


# Allowed characters for UCI identifiers.
UCI_IDENTIFIER = re.compile(r'^[a-zA-Z0-9_]+$')
UCI_PACKAGE_IDENTIFIER = re.compile(r'^[a-zA-Z0-9_-]+$')


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

    def __init__(self, key=None, typ=None, managed_by=None):
        """
        Class constructor.
        """

        if not isinstance(managed_by, list):
            managed_by = [managed_by]

        self.__dict__['_key'] = key
        self.__dict__['_typ'] = typ
        self.__dict__['_managed_by'] = managed_by
        self.__dict__['_values'] = collections.OrderedDict()

    def __setattr__(self, name, value):
        """
        Sets a configuration attribute.
        """

        if not name.startswith('_') and not UCI_IDENTIFIER.match(name):
            raise ValueError("Invalid UCI identifier '%s'." % name)

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

    __setitem__ = __setattr__
    __delitem__ = __delattr__
    __getitem__ = __getattr__

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

    def get_manager(self, klass=None):
        """
        Returns a manager object in case one has been set when adding this
        piece of configuration.
        """

        if not self._managed_by:
            return None

        for manager in self._managed_by:
            if klass is None or isinstance(manager, klass):
                return manager

        return None

    def add_manager(self, manager):
        """
        Adds a new manager.
        """

        self._managed_by.append(manager)

    def matches(self, attribute, value):
        """
        Returns true if this section's attribute matches a specific value.
        """

        if attribute == '_managed_by':
            return value in self._managed_by

        return getattr(self, attribute, None) == value

    def format_value(self, key, value, package, section, idx=None, fmt=UCIFormat.DUMP):
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
                return ['{0}.{1}.{2}={3}'.format(package, section, key, value)]
            else:
                return ['{0}.@{1}[{2}].{3}={4}'.format(package, section, idx, key, value)]
        elif fmt == UCIFormat.FILES:
            if isinstance(value, (list, tuple)):
                return ['\tlist %s \'%s\'' % (key, item) for item in value]
            elif isinstance(value, bool):
                return ['\toption %s \'%s\'' % (key, int(value))]
            else:
                return ['\toption %s \'%s\'' % (key, str(value).strip().replace('\n', ' '))]

        return str(value)

    def format(self, package, section, idx=None, fmt=UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """

        output = []

        # Output section header
        if self._typ is not None:
            # Named sections
            if fmt == UCIFormat.DUMP:
                output.append('{0}.{1}={2}'.format(package, section, self._typ))
            elif fmt == UCIFormat.FILES:
                output.append('config %s \'%s\'' % (self._typ, section))
        else:
            # Ordered sections
            if fmt == UCIFormat.DUMP:
                output.append('{0}.@{1}[{2}]={1}'.format(package, section, idx))
            elif fmt == UCIFormat.FILES:
                output.append('config %s' % section)

        # Output section values
        for key, value in self._values.iteritems():
            if key.startswith('_'):
                continue
            output += self.format_value(key, value, package, section, idx, fmt)

        # Output section footer
        if fmt == UCIFormat.FILES:
            output.append('')

        return output


class UCIPackage(object):
    """
    Represents an UCI configuration file with multiple named and ordered
    sections.
    """

    def __init__(self, package):
        """
        Class constructor.

        :param package: Package name
        """

        if not UCI_PACKAGE_IDENTIFIER.match(package):
            raise ValueError("Invalid UCI package name '%s'." % package)

        self._package = package
        self._named_sections = collections.OrderedDict()
        self._ordered_sections = collections.OrderedDict()

    def add(self, *args, **kwargs):
        """
        Creates a new UCI section. An ordered section should be specified by using
        a single argument and a named section by using a single keyword argument.

        :return: The newly created UCISection
        """

        managed_by = kwargs.pop('managed_by', None)

        if len(args) > 1 or len(kwargs) > 1 or len(args) == len(kwargs):
            raise ValueError

        if kwargs:
            # Adding a named section.
            section_key = kwargs.values()[0]
            section_type = kwargs.keys()[0]
            if not UCI_IDENTIFIER.match(section_key):
                raise ValueError("Invalid named UCI section name '%s'." % section_key)

            section = UCISection(key=section_key, typ=section_type, managed_by=managed_by)

            # Check for duplicates to avoid screwing up existing lists and sections
            if section_key in self._named_sections:
                raise ValueError("UCI section '%s' is already defined!" % section_key)

            self._named_sections[section_key] = section
        else:
            # Adding an ordered section.
            section = UCISection(managed_by=managed_by)
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

        sections = self.find_all_named_sections(section_type, **query)
        if not sections:
            return None

        return sections[0]

    def find_all_named_sections(self, section_type, **query):
        """
        Searches for all named sections having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: A list of named sections matching the criteria
        """

        sections = []
        for name, section in self.named_sections():
            if section.get_type() != section_type:
                continue

            if all((section.matches(a, v) for a, v in query.items())):
                sections.append(section)

        return sections

    def find_ordered_section(self, section_type, **query):
        """
        Searches for the first ordered section having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: Ordered section or None if not found
        """

        sections = self.find_all_ordered_sections(section_type, **query)
        if not sections:
            return None

        return sections[0]

    def find_all_ordered_sections(self, section_type, **query):
        """
        Searches for all ordered section having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: List of ordered sections matching the criteria
        """

        sections = []
        for section in self._ordered_sections.get(section_type, []):
            if all((section.matches(a, v) for a, v in query.items())):
                sections.append(section)

        return sections

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

    def __getitem__(self, section):
        try:
            return self.__getattr__(section)
        except AttributeError:
            raise KeyError(section)

    def format(self, fmt=UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.

        :param fmt: Wanted export format
        """

        output = []
        for name, section in self._named_sections.iteritems():
            output += section.format(self._package, name, fmt=fmt)

        for name, sections in self._ordered_sections.iteritems():
            for idx, section in enumerate(sections):
                output += section.format(self._package, name, idx, fmt=fmt)

        return output


class OpenWrtCryptoManager(cgm_base.PlatformCryptoManager):
    class CryptoObject(cgm_base.PlatformCryptoManager.CryptoObject):
        def __init__(self, *args, **kwargs):
            super(OpenWrtCryptoManager.CryptoObject, self).__init__(*args, **kwargs)

            # If path is never requested, we will not generate a file at all.
            self._path = None

        def path(self):
            """
            Returns the path to the crypto object.
            """

            type_map = {
                cgm_base.PlatformCryptoManager.CERTIFICATE: 'certificate',
                cgm_base.PlatformCryptoManager.PUBLIC_KEY: 'public_key',
                cgm_base.PlatformCryptoManager.PRIVATE_KEY: 'private_key',
                cgm_base.PlatformCryptoManager.SYMMETRIC_KEY: 'symmetric_key',
                cgm_base.PlatformCryptoManager.SSH_AUTHORIZED_KEY: 'ssh_authorized_key',
            }
            self._path = '/etc/crypto/%s/%s' % (type_map[self.object_type], self.name)
            return self._path

        def get_config(self):
            """
            Returns a configuration dictionary suitable for use in JSON
            documents.
            """

            config = super(OpenWrtCryptoManager.CryptoObject, self).get_config()
            config.update({
                'path': self._path,
            })

            return config

    object_class = CryptoObject


class OpenWrtSysctlManager(object):
    """
    OpenWrt-specific sysctl manager.
    """

    def __init__(self):
        """
        Class constructor.
        """

        self._settings = {}

    def set_variable(self, key, value):
        """
        Sets a sysctl variable.

        :param key: Variable key
        :param value: Variable value
        """

        self._settings[key] = value

    def get_config(self):
        """
        Returns sysctl configuration suitable for use in JSON documents.
        """

        return self._settings


class UCIConfiguration(cgm_base.PlatformConfiguration):
    """
    An in-memory implementation of UCI configuration.
    """

    crypto_manager_class = OpenWrtCryptoManager
    sysctl_manager_class = OpenWrtSysctlManager

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        super(UCIConfiguration, self).__init__(*args, **kwargs)
        self.sysctl = self.sysctl_manager_class()
        self._packages = {}

    def package_version_compare(self, version_a, version_b):
        """
        Platform-specific version check. Should return an integer, which is
        less than, equal to or greater than zero, based on the result of the
        comparison.

        :param version_a: First version
        :param version_b: Second version
        """

        if apt_version_compare is not None:
            return apt_version_compare(version_a, version_b)
        else:
            raise NotImplementedError('Version comparison functions are not available.')

    def get_build_config(self):
        """
        Returns a build configuration which must be JSON-serializable. This
        configuration will be passed to the backend builder function and must
        contain anything that the builder will need to configure the generated
        firmware.
        """

        result = self.format(fmt=UCIFormat.FILES)
        result.update(super(UCIConfiguration, self).get_build_config())
        result.update({
            '_sysctl': self.sysctl.get_config(),
        })
        return result

    def __getattr__(self, package):
        """
        Returns the desired UCI package (config file).
        """

        if package.startswith('__') and package.endswith('__'):
            raise AttributeError(package)

        return self._packages.setdefault(package, UCIPackage(package))

    __getitem__ = __getattr__

    def format(self, fmt=UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.

        :param fmt: Wanted export format
        """

        if fmt == UCIFormat.DUMP:
            # UCI dump format
            output = []
            for name, package in self._packages.iteritems():
                output += package.format(fmt=fmt)
        elif fmt == UCIFormat.FILES:
            # UCI split into multiple files
            output = {}
            for name, package in self._packages.iteritems():
                output[name] = '\n'.join(package.format(fmt=fmt))

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

# NAT routing table.
NAT_ROUTING_TABLE_ID = 100
NAT_ROUTING_TABLE_NAME = 'nat'
NAT_ROUTING_TABLE_PRIORITY = 600


@cgm_base.register_platform_module('openwrt', 10)
def general(node, cfg):
    """
    General configuration for nodewatcher firmware.
    """

    system = cfg.system.add('system')
    system.hostname = node.config.core.general().name
    system.uuid = node.uuid
    # Enable bigger logs by default.
    system.log_size = 256

    try:
        zone = node.config.core.location().timezone.zone
        system.timezone = posix_tz.get_posix_tz(zone)
        if not system.timezone:
            raise cgm_base.ValidationError(_("Unsupported OpenWRT timezone '%s'!") % zone)
    except (registry_exceptions.RegistryItemNotRegistered, AttributeError):
        system.timezone = posix_tz.get_posix_tz(settings.TIME_ZONE)
        if not system.timezone:
            system.timezone = 'UTC'

    # Reboot system in 3 seconds after a kernel panic.
    cfg.sysctl.set_variable('kernel.panic', 3)


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
        # If there is no password authentication, we still need to create a default root account
        # as otherwise authentication will not be possible. In this case, we use a random password.
        cfg.accounts.add_user('root', crypto.get_random_string(), 0, 0, '/tmp', '/bin/ash')


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

    if section._uplink:
        # An uplink interface cannot be used for routing.
        if getattr(interface, 'routing_protocols', []):
            raise cgm_base.ValidationError(_("An uplink interface cannot also be used for routing!"))

        # Ensure that uplink traffic is routed via the main table.
        policy = cfg.network.add('rule')
        policy['in'] = iface_name
        policy.lookup = 'main'
        policy.priority = 500

        # Configure firewall policy for the uplink interface.
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
    if switch_iface is None:
        raise cgm_base.ValidationError(
            _("No mapping for OpenWrt when configuring switch '%(switch)s'.") % {'switch': port.switch}
        )

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
        if port.is_tagged(p) or (p in switch.cpu_ports and switch.cpu_tagged):
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
def usb(node, cfg):
    """
    Install USB modules for devices which support it.
    """

    device = node.config.core.general().get_device()
    if not device:
        return

    if device.usb:
        # Include base USB packages for devices supporting USB.
        # TODO: Perhaps this should be made device-specific so only the needed packages are installed.
        cfg.packages.update([
            'kmod-usb2',
            'kmod-usb-ohci',
            'kmod-usb-uhci',
        ])


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

    # Obtain the device descriptor for this device and generate physical port resource so
    # we can track binding of ports to different interface and prevent multiple definitions.
    device = node.config.core.general().get_device()
    if not device:
        return

    cfg.resources.add(cgm_resources.PhysicalPortResource(
        'ethernet',
        [port.identifier for port in device.ports],
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
            iface_name = device.get_bridge_mapping('openwrt', interface)
            iface = cfg.network.add(interface=iface_name, managed_by=interface)
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

            configure_interface(cfg, node, interface, iface, iface_name)
        elif isinstance(interface, cgm_models.MobileInterfaceConfig):
            # Check if the device actually supports USB.
            if not device.usb:
                raise cgm_base.ValidationError(
                    _("The target device does not support USB, so mobile interface cannot be configured!")
                )

            iface_name = interface.device.replace('-', '')
            iface = cfg.network.add(interface=iface_name, managed_by=interface)

            if interface.uplink:
                iface._uplink = True
                set_dhcp_ignore(cfg, iface_name)

            if interface.device.startswith('eth'):
                # Mobile modem presents itself as a USB ethernet device. Determine the port based on
                # the existing device port map to see which interfaces are already there by default.
                used_ports = set()
                for port in device.port_map['openwrt'].values():
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

            # Check if we need to configure the switch.
            port = device.get_port(interface.eth_port)
            if isinstance(port, cgm_devices.SwitchedEthernetPort):
                configure_switch(cfg, device, port)

            if check_interface_bridged(interface) is not None:
                continue

            try:
                iface = cfg.network.add(interface=interface.eth_port, managed_by=interface)
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

            configure_interface(cfg, node, interface, iface, interface.eth_port)
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
                wifi_radio = device.remap_port('openwrt', interface.wifi_radio)
                if not wifi_radio:
                    raise cgm_base.ValidationError(
                        _("Radio '%s' not defined on OpenWRT!") % interface.wifi_radio
                    )

                try:
                    radio_type = device.drivers['openwrt'][interface.wifi_radio]
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
                vif_name = device.get_vif_mapping('openwrt', interface.wifi_radio, vif)
                wif.ifname = vif_name

                bridge = check_interface_bridged(vif)
                if bridge is not None:
                    # Wireless interfaces are reverse-configured to be part of a bridge
                    wif.network = bridge.name
                else:
                    iface = cfg.network.add(interface=vif_name, managed_by=vif)
                    wif.network = vif_name

                    if vif.uplink:
                        if vif.mode != 'sta':
                            raise cgm_base.ValidationError(_("Wireless interface may only be an uplink when in station mode!"))

                        iface._uplink = True
                        set_dhcp_ignore(cfg, vif_name)

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

import copy
import inspect

from django.core import exceptions

from ...registry import registration


class RouterPort(object):
    """
    An abstract descriptor of a router port.
    """

    def __init__(self, identifier, description):
        """
        Class constructor.
        """
        self.identifier = identifier
        self.description = description


class EthernetPort(RouterPort):
    """
    Describes a router's ethernet port.
    """

    pass


class SwitchedEthernetPort(EthernetPort):
    """
    Describes a router's ethernet port attached to a configurable
    switch.
    """

    def __init__(self, identifier, description, switch, vlan, ports):
        """
        Class constructor.
        """

        super(SwitchedEthernetPort, self).__init__(identifier, description)
        self.switch = switch
        self.vlan = vlan
        self.ports = ports

    def validate(self, router):
        """
        Ensure that the switch that the port refers to actually exists.
        """

        switch = router.get_switch(self.switch)
        if switch is None:
            raise exceptions.ImproperlyConfigured("Switched ethernet port '%s' refers to an invalid switch '%s'!" % (
                self.identifier, self.switch
            ))

        if not (0 <= self.vlan < switch.vlans):
            raise exceptions.ImproperlyConfigured("Switched ethernet port '%s' VLAN (%s) out of range!" % (
                self.identifier, self.vlan
            ))

        if switch.cpu_port not in self.ports:
            raise exceptions.ImproperlyConfigured("Switched ethernet port '%s' does not connect to CPU!" % (
                self.identifier
            ))

        for port in self.ports:
            if port not in switch.ports:
                raise exceptions.ImproperlyConfigured("Switched ethernet port '%s' contains invalid port '%d'!" % (
                    self.identifier, port
                ))


class AntennaConnector(object):
    """
    An antenna connector that is present on a specific radio.
    """

    def __init__(self, identifier, description):
        """
        Class constructor.
        """
        self.identifier = identifier
        self.description = description


class RouterRadio(object):
    """
    An abstract descriptor of a router radio.
    """

    def __init__(self, identifier, description, protocols, connectors):
        """
        Class constructor.
        """

        self.identifier = identifier
        self.description = description
        self.protocols = protocols
        self.connectors = connectors
        self.index = None

    def get_connector_choices(self):
        """
        Returns a list of antenna connector choices for this radio.
        """

        return ((c.identifier, c.description) for c in self.connectors)

    def get_protocol_choices(self):
        """
        Returns a list of protocol choices for this radio.
        """

        return ((p.identifier, p.description) for p in self.protocols)

    def get_protocol(self, identifier):
        """
        Returns the protocol descriptor for a given identifier.

        :param identifier: Protocol descriptor
        """

        for protocol in self.protocols:
            if protocol.identifier == identifier:
                return protocol


class IntegratedRadio(RouterRadio):
    """
    Describes a router's integrated radio.
    """

    pass


class MiniPCIRadio(RouterRadio):
    """
    Describes a router's MiniPCI slot for a radio.
    """

    pass


class InternalAntenna(object):
    """
    Describes an antenna that comes with the router by default.
    """

    def __init__(self, identifier, polarization, angle_horizontal, angle_vertical, gain):
        """
        Class constructor.
        """

        self.identifier = identifier
        self.polarization = polarization
        self.angle_horizontal = angle_horizontal
        self.angle_vertical = angle_vertical
        self.gain = gain


class Switch(object):
    """
    Describes an ethernet switch that a router has.
    """

    def __init__(self, identifier, description, ports, cpu_port, vlans):
        """
        Class constructor.
        """

        self.identifier = identifier
        self.description = description

        if isinstance(ports, int):
            ports = range(ports)

        self.ports = ports
        if cpu_port not in ports:
            raise exceptions.ImproperlyConfigured("Switch descriptor '%s' refers to an invalid CPU port '%s'!" % (
                self.identifier, cpu_port
            ))

        self.cpu_port = cpu_port
        self.vlans = vlans


class Features(object):
    """
    Represents features a router can have.
    """

    MultipleSSID = "multiple_ssid"

# A list of attributes that are required to be defined
REQUIRED_ROUTER_ATTRIBUTES = {
    'identifier',
    'name',
    'manufacturer',
    'url',
    'architecture',
    'radios',
    'switches',
    'ports',
    'antennas',
}


class RouterMetaclass(type):
    """
    Type for router descriptors.
    """

    def __new__(cls, name, bases, attrs):
        """
        Creates a new RouterBase class.
        """

        new_class = type.__new__(cls, name, bases, attrs)

        if name != 'RouterBase':
            # Validate the presence of all attributes
            required_attrs = copy.deepcopy(REQUIRED_ROUTER_ATTRIBUTES)
            for attr in REQUIRED_ROUTER_ATTRIBUTES:
                if getattr(new_class, attr, None) is None:
                    raise exceptions.ImproperlyConfigured("Attribute '{0}' is required for router descriptor specification!".format(attr))

            # Validate that list of switches only contains Switch instances
            if len([x for x in new_class.switches if not isinstance(x, Switch)]):
                raise exceptions.ImproperlyConfigured("List of router switches may only contain Switch instances!")

            # Router ports and radios cannot both be empty
            if not len(new_class.radios) and not len(new_class.ports):
                raise exceptions.ImproperlyConfigured("A router cannot be without radios and ports!")

            # Validate that list of ports only contains RouterPort instances and validate
            # that switched ports refer to valid switches
            for port in new_class.ports:
                if not isinstance(port, RouterPort):
                    raise exceptions.ImproperlyConfigured("List of router ports may only contain RouterPort instances!")

                if hasattr(port, 'validate'):
                    port.validate(new_class)

            # Validate that list of radios only contains RouterRadio instances and assign
            # radio indices
            for idx, radio in enumerate(new_class.radios):
                if not isinstance(radio, RouterRadio):
                    raise exceptions.ImproperlyConfigured("List of router radios may only contain RouterRadio instances!")

                radio.index = idx

            # Validate that list of antennas only contains InternalAntenna instances
            if len([x for x in new_class.antennas if not isinstance(x, InternalAntenna)]):
                raise exceptions.ImproperlyConfigured("List of router antennas may only contain InternalAntenna instances!")

        return new_class


class RouterBase(object):
    """
    An abstract router hardware descriptor.
    """

    __metaclass__ = RouterMetaclass

    features = []
    port_map = {}
    drivers = {}
    profiles = {}
    identifier = None
    manufacturer = None
    name = None
    ports = None
    radios = None
    switches = None

    @classmethod
    def register(cls, platform):
        """
        Performs router model registration.

        :param platform: Platform instance
        """

        # Register a new choice in the configuration registry
        registration.point('node.config').register_choice(
            'core.general#router',
            cls.identifier,
            '%s :: %s' % (cls.manufacturer, cls.name),
            limited_to=('core.general#platform', platform.name),
        )

        # Register a new choice for available router ports
        for port in cls.ports:
            registration.point('node.config').register_choice(
                'core.interfaces#eth_port',
                port.identifier,
                port.description,
                limited_to=('core.general#router', cls.identifier),
            )

        # Register a new choice for available router radios
        for radio in cls.radios:
            registration.point('node.config').register_choice(
                'core.interfaces#wifi_radio',
                radio.identifier,
                radio.description,
                limited_to=('core.general#router', cls.identifier),
            )

        # Register CGM methods
        for _, function in inspect.getmembers(cls, inspect.isfunction):
            if not getattr(function, 'cgm_module', False):
                continue

            if function.cgm_module_platform is None or function.cgm_module_platform == platform.name:
                platform.register_module(
                    function.cgm_module_weight,
                    function,
                    cls.identifier,
                )

    @classmethod
    def remap_port(cls, platform, port):
        """
        Remaps a port according to the port mapping.

        :param platform: Platform identifier
        :param port: Port identifier
        """

        return cls.port_map.get(platform, {}).get(port, None)

    def __init__(self):
        """
        Prevent instantiation of this class.
        """

        raise TypeError("Router model descriptors are non-instantiable!")

    def __setattr__(self, key, value):
        """
        Prevent modification of router model descriptors.
        """

        raise AttributeError("Router model descriptors are immutable!")

    @classmethod
    def get_radio(cls, identifier):
        """
        Returns a radio descriptor with the specified identifier.

        :param identifier: Radio identifier
        """

        for radio in cls.radios:
            if radio.identifier == identifier:
                return radio

    @classmethod
    def get_switch(cls, identifier):
        """
        Returns a switch descriptor with the specified identifier.

        :param identifier: Port identifier
        """

        for switch in cls.switches:
            if switch.identifier == identifier:
                return switch

    @classmethod
    def get_port(cls, identifier):
        """
        Returns a port descriptor with the specified identifier.

        :param identifier: Port identifier
        """

        for port in cls.ports:
            if port.identifier == identifier:
                return port


def register_module(platform=None, weight=50):
    """
    Marks a method to be registered as a CGM upon router registration.
    """

    def wrapper(f):
        f.cgm_module = True
        f.cgm_module_weight = weight
        f.cgm_module_platform = platform
        return staticmethod(f)

    return wrapper

import inspect

from django.core import exceptions
from django.utils.translation import ugettext as _

from ...registry import registration
from . import protocols as cgm_protocols


class DevicePort(object):
    """
    An abstract descriptor of a device port.
    """

    def __init__(self, identifier, description):
        """
        Class constructor.
        """
        self.identifier = identifier
        self.description = description


class EthernetPort(DevicePort):
    """
    Describes a device's ethernet port.
    """

    pass


class SwitchedEthernetPort(EthernetPort):
    """
    Describes a device's ethernet port attached to a configurable
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

    def validate(self, device):
        """
        Ensure that the switch that the port refers to actually exists.
        """

        switch = device.get_switch(self.switch)
        if switch is None:
            raise exceptions.ImproperlyConfigured("Switched ethernet port '%s' refers to an invalid switch '%s'!" % (
                self.identifier, self.switch
            ))

        if not (0 <= self.vlan < switch.vlans):
            raise exceptions.ImproperlyConfigured("Switched ethernet port '%s' VLAN (%s) out of range!" % (
                self.identifier, self.vlan
            ))

        if not switch.cpu_ports.intersection(self.ports):
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


class DeviceRadio(object):
    """
    An abstract descriptor of a device's radio.
    """

    # Radio features
    MultipleSSID = "multiple_ssid"

    def __init__(self, identifier, description, protocols, connectors, features=None):
        """
        Class constructor.
        """

        self.identifier = identifier
        self.description = description
        self.protocols = protocols
        self.connectors = connectors
        self.features = features or []
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

    def has_feature(self, feature):
        """
        Returns true if this radio has a specific feature.
        """

        return feature in self.features


class IntegratedRadio(DeviceRadio):
    """
    Describes a device's integrated radio.
    """

    pass


class USBRadio(DeviceRadio):
    """
    Describes a device's USB radio.
    """

    def __init__(self, identifier, description):
        """
        Class constructor.
        """

        super(USBRadio, self).__init__(
            identifier,
            description,
            # USB radios must always support all protocols.
            [
                cgm_protocols.IEEE80211BGN(
                    cgm_protocols.IEEE80211BGN.SHORT_GI_20,
                    cgm_protocols.IEEE80211BGN.SHORT_GI_40,
                    cgm_protocols.IEEE80211BGN.RX_STBC1,
                    cgm_protocols.IEEE80211BGN.DSSS_CCK_40,
                ),
                cgm_protocols.IEEE80211AN(
                    cgm_protocols.IEEE80211AN.SHORT_GI_40,
                    cgm_protocols.IEEE80211AN.TX_STBC1,
                    cgm_protocols.IEEE80211AN.RX_STBC1,
                    cgm_protocols.IEEE80211AN.DSSS_CCK_40,
                )
            ],
            # Connectors.
            [
                AntennaConnector('%sa0' % identifier, "Antenna0"),
            ],
            # Features.
            [
                DeviceRadio.MultipleSSID,
            ],
        )


class MiniPCIRadio(DeviceRadio):
    """
    Describes a device's MiniPCI slot for a radio.
    """

    pass


class InternalAntenna(object):
    """
    Describes an antenna that comes with the device by default.
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
    Describes an ethernet switch that a device has.
    """

    def __init__(self, identifier, description, ports, cpu_port, vlans, cpu_tagged=False):
        """
        Class constructor.
        """

        self.identifier = identifier
        self.description = description

        if isinstance(ports, int):
            ports = range(ports)

        self.ports = ports
        if not isinstance(cpu_port, (list, tuple)):
            cpu_ports = set([cpu_port])
        else:
            cpu_ports = set(cpu_port)

        for cpu_port in cpu_ports:
            if cpu_port not in ports:
                raise exceptions.ImproperlyConfigured("Switch descriptor '%s' refers to an invalid CPU port '%s'!" % (
                    self.identifier, cpu_port
                ))

        self.cpu_ports = cpu_ports
        self.vlans = vlans
        self.cpu_tagged = cpu_tagged

# A list of attributes that are required to be defined
REQUIRED_DEVICE_ATTRIBUTES = (
    'identifier',
    'name',
    'manufacturer',
    'url',
    'architecture',
    'radios',
    'switches',
    'ports',
    'antennas',
)


class DeviceMetaclass(type):
    """
    Type for device descriptors.
    """

    def __new__(cls, name, bases, attrs):
        """
        Creates a new DeviceBase class.
        """

        new_class = type.__new__(cls, name, bases, attrs)

        if name != 'DeviceBase':
            # Validate the presence of all attributes
            for attr in REQUIRED_DEVICE_ATTRIBUTES:
                if getattr(new_class, attr, None) is None:
                    raise exceptions.ImproperlyConfigured("Attribute '{0}' is required for device descriptor specification!".format(attr))

            # If USB devices are supported, automatically configure a radio.
            if getattr(new_class, 'usb', False):
                if not new_class.get_radio('wifi-usb0'):
                    new_class.radios.append(USBRadio('wifi-usb0', "USB wireless radio"))

            # Validate that list of switches only contains Switch instances
            if len([x for x in new_class.switches if not isinstance(x, Switch)]):
                raise exceptions.ImproperlyConfigured("List of device switches may only contain Switch instances!")

            # Router ports and radios cannot both be empty
            if not len(new_class.radios) and not len(new_class.ports):
                raise exceptions.ImproperlyConfigured("A device cannot be without radios and ports!")

            # Validate that list of ports only contains DevicePort instances and validate
            # that switched ports refer to valid switches
            for port in new_class.ports:
                if not isinstance(port, DevicePort):
                    raise exceptions.ImproperlyConfigured("List of device ports may only contain DevicePort instances!")

                if hasattr(port, 'validate'):
                    port.validate(new_class)

            # Validate that list of radios only contains DeviceRadio instances and assign
            # radio indices
            for idx, radio in enumerate(new_class.radios):
                if not isinstance(radio, DeviceRadio):
                    raise exceptions.ImproperlyConfigured("List of device radios may only contain DeviceRadio instances!")

                radio.index = idx

            # Validate that list of antennas only contains InternalAntenna instances
            if len([x for x in new_class.antennas if not isinstance(x, InternalAntenna)]):
                raise exceptions.ImproperlyConfigured("List of device antennas may only contain InternalAntenna instances!")

        return new_class


class DeviceBase(object):
    """
    An abstract device hardware descriptor.
    """

    __metaclass__ = DeviceMetaclass

    port_map = {}
    drivers = {}
    profiles = {}
    identifier = None
    manufacturer = None
    name = None
    ports = None
    radios = None
    switches = None
    usb = False

    @classmethod
    def register(cls, platform):
        """
        Performs device model registration.

        :param platform: Platform instance
        """

        # Register a new choice in the configuration registry
        registration.point('node.config').register_choice(
            'core.general#router',
            registration.Choice(
                cls.identifier,
                _("%(manufacturer)s - %(name)s") % {'manufacturer': cls.manufacturer, 'name': cls.name},
                limited_to=('core.general#platform', platform.name),
            )
        )

        # Register a new choice for available device ports
        for port in cls.ports:
            registration.point('node.config').register_choice(
                'core.interfaces#eth_port',
                registration.Choice(
                    port.identifier,
                    port.description,
                    limited_to=('core.general#router', cls.identifier),
                )
            )

        # Register a new choice for available device radios
        for radio in cls.radios:
            registration.point('node.config').register_choice(
                'core.interfaces#wifi_radio',
                registration.Choice(
                    radio.identifier,
                    radio.description,
                    limited_to=('core.general#router', cls.identifier),
                )
            )

        # Register CGM methods
        for name, function in inspect.getmembers(cls, inspect.isfunction):
            if not getattr(function, 'cgm_module', False):
                continue

            if function.cgm_module_platform is None or function.cgm_module_platform == platform.name:
                platform.register_module(
                    function.cgm_module_weight,
                    function,
                    cls.identifier,
                )

    @classmethod
    def remap_port(cls, platform, interface_or_port):
        """
        Remaps a port according to the port mapping.

        :param platform: Platform identifier
        :param interface_or_port: Interface model or port identifier
        """

        from . import models as cgm_models

        if isinstance(interface_or_port, cgm_models.EthernetInterfaceConfig):
            interface_or_port = interface_or_port.eth_port
        elif isinstance(interface_or_port, cgm_models.WifiRadioDeviceConfig):
            interface_or_port = interface_or_port.wifi_radio

        return cls.port_map.get(platform, {}).get(interface_or_port, None)

    @classmethod
    def get_vif_mapping(cls, platform, radio, vif):
        """
        Returns a name for the wireless virtual interface.

        :param platform: Platform identifier
        :param radio: Radio identifier
        :param vif: Wireless virtual interface model
        """

        return ('%s%d' % (vif.mode, vif.get_index())).lower().replace(' ', '')

    @classmethod
    def get_bridge_mapping(cls, platform, bridge):
        """
        Returns a bridge name.

        :param platform: Platform identifier
        :param bridge: Bridge interface model
        """

        return bridge.name.lower().replace(' ', '')

    def __init__(self):
        """
        Prevent instantiation of this class.
        """

        raise TypeError("Router model descriptors are non-instantiable!")

    def __setattr__(self, key, value):
        """
        Prevent modification of device model descriptors.
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
    Marks a method to be registered as a CGM upon device registration.
    """

    def wrapper(f):
        f.cgm_module = True
        f.cgm_module_weight = weight
        f.cgm_module_platform = platform
        return staticmethod(f)

    return wrapper

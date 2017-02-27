import copy
import inspect

from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

from ...registry import registration
from . import protocols as cgm_protocols

# Separator between VLAN atoms in switch port identifiers.
SWITCH_ATOM_SEPARATOR = '.'


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

    def __init__(self, identifier, description, protocols, connectors, features=None, index=None):
        """
        Class constructor.
        """

        self.identifier = identifier
        self.description = description
        self.protocols = protocols
        self.connectors = connectors
        self.features = features or []
        self.index = index

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

    def __init__(self, identifier, description, index=None):
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
            index=index
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


class SwitchVLANPreset(object):
    """
    Describes a device's ethernet port attached to a configurable
    switch.
    """

    def __init__(self, identifier, description, vlan, ports):
        """
        Class constructor.
        """

        self.identifier = identifier
        self.description = description
        self.switch = None
        self.vlan = vlan
        self.ports = ports

    def attach(self, switch):
        """
        Attaches this VLAN preset to a specific switch. It is an error to attempt
        to attach an already attached port to a differnet switch.

        :param switch: Switch instance to attach to
        """

        if self.switch is not None and self.switch != switch:
            raise ValueError('Cannot reattach already attached SwitchVLANPreset')

        # Validate configuration.
        if self.vlan not in switch.vlans:
            raise exceptions.ImproperlyConfigured("Switch VLAN preset '%s' VLAN (%s) out of range!" % (
                self.identifier, self.vlan
            ))

        if not switch.cpu_ports.intersection(self.ports):
            raise exceptions.ImproperlyConfigured("Switch VLAN preset '%s' does not connect to CPU!" % (
                self.identifier
            ))

        for port in self.ports:
            if port not in switch.ports:
                raise exceptions.ImproperlyConfigured("Switch VLAN preset '%s' contains invalid port '%d'!" % (
                    self.identifier, port
                ))

        self.switch = switch


class SwitchPreset(object):
    """
    Describes a switch VLAN preset.
    """

    def __init__(self, identifier, description, vlans=None, custom=False):
        self.identifier = identifier
        self.description = description
        self.vlans = vlans or []
        self.custom = custom

    def attach(self, switch):
        """
        Attaches this switch preset to a switch.
        """

        for vlan in self.vlans:
            vlan.attach(switch)


class Switch(object):
    """
    Describes an ethernet switch that a device has.
    """

    def __init__(self, identifier, description, ports, cpu_port, vlans, cpu_tagged=False,
                 configurable=True, presets=None, tagged_ports=None):
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
        if isinstance(vlans, int):
            self.vlans = range(1, vlans + 1)
        elif isinstance(vlans, dict):
            self.vlans = range(vlans['start'], vlans['end'] + 1)
        else:
            raise exceptions.ImproperlyConfigured("Switch descriptor '%s' has invalid VLANs specification." % (
                self.identifier
            ))
        self.cpu_tagged = cpu_tagged
        self.configurable = configurable
        self.tagged_ports = tagged_ports or []
        if cpu_tagged:
            self.tagged_ports.extend(cpu_ports)

        # Validate presets.
        self.presets = []
        has_default_preset = False
        if presets is not None:
            if not isinstance(presets, (list, tuple)):
                raise exceptions.ImproperlyConfigured("Presets for switch '%s' must be a list or tuple!" % self.identifier)

            names = set()
            for preset in presets:
                if preset.identifier in names:
                    raise exceptions.ImproperlyConfigured("Preset identifier '%s' is duplicated in switch '%s'!" % (
                        preset.identifier, self.identifier
                    ))

                if preset.custom:
                    raise exceptions.ImproperlyConfigured(
                        "Preset '%s' cannot be marked as custom. Set configurable=True for the switch instead." % (
                            preset.identifier
                        )
                    )

                names.add(preset.identifier)

                # Attach VLAN preset to this switch.
                preset.attach(self)

            has_default_preset = 'default' in names
            self.presets.extend(presets)

        if not has_default_preset:
            raise exceptions.ImproperlyConfigured("Switch '%s' does not have a default preset defined!" % (
                self.identifier
            ))

        # Configurable switches support custom configuration.
        if configurable:
            self.presets.append(SwitchPreset('custom', _("Custom VLAN configuration"), custom=True))

    def is_tagged(self, port):
        """
        Returns true if the given port must be tagged.

        :param port: Port identifier
        """

        return port in self.tagged_ports

    def get_preset(self, identifier):
        """
        Returns the preset with the given identifier.
        """

        for preset in self.presets:
            if preset.identifier == identifier:
                return preset

    def get_preset_choices(self):
        """
        Returns a list of VLAN presets for this switch.
        """

        return ((p.identifier, p.description) for p in self.presets)

    def get_vlan_choices(self):
        """
        Returns a list of available VLANs for this switch.
        """

        return ((vlan, _("VLAN %s") % vlan) for vlan in self.vlans)

    def get_port_choices(self):
        """
        Returns a list of available ports for this switch.
        """

        # TODO: Should we support better port names, similar to ethernet interfaces?
        def port_name(port):
            if port in self.cpu_ports:
                return _("Port %s (CPU)") % port

            return _("Port %s") % port

        return ((port, port_name(port)) for port in self.ports)

    def get_port_identifier(self, vlan):
        """
        Returns a unique port identifier for a specific switch port.
        """

        return '{switch}{separator}vlan{vlan}'.format(
            separator=SWITCH_ATOM_SEPARATOR,
            switch=self.identifier,
            vlan=vlan,
        )

    def get_vlan_from_identifier(self, atom):
        """
        Returns the VLAN identifier given the last atom from an identifier previously
        returned by `get_port_identifier`.
        """

        return int(atom[len('vlan'):])


class SwitchPortMap(object):
    """
    Describes a port mapping for a given switch. Port mappings are defined for
    each supported platform.
    """

    def __init__(self, switch, vlans):
        """
        Class constructor.

        :param switch: Switch name mapping
        :param vlans: VLAN port mapping pattern
        """

        self.switch = switch
        self.vlans = vlans

    def get_port(self, vlan):
        """
        Returns a mapping for the given VLAN.

        :param vlan: VLAN number
        :return: Mapping
        """

        return self.vlans.format(vlan=vlan)

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

            new_class.switches = copy.deepcopy(new_class.switches)

            # Router ports and radios cannot both be empty
            if not new_class.radios and not new_class.ports and not new_class.switches:
                raise exceptions.ImproperlyConfigured("A device cannot be without radios, ports and switches!")

            # Validate that list of ports only contains DevicePort instances and validate
            # that switched ports refer to valid switches
            for port in new_class.ports:
                if not isinstance(port, DevicePort):
                    raise exceptions.ImproperlyConfigured("List of device ports may only contain DevicePort instances!")

                if hasattr(port, 'validate'):
                    port.validate(new_class)

            new_class.ports = copy.deepcopy(new_class.ports)

            # Validate that list of radios only contains DeviceRadio instances and assign
            # radio indices
            for idx, radio in enumerate(new_class.radios):
                if not isinstance(radio, DeviceRadio):
                    raise exceptions.ImproperlyConfigured("List of device radios may only contain DeviceRadio instances!")

                if radio.index is None:
                    radio.index = idx

            # Validate that list of antennas only contains InternalAntenna instances
            if len([x for x in new_class.antennas if not isinstance(x, InternalAntenna)]):
                raise exceptions.ImproperlyConfigured("List of device antennas may only contain InternalAntenna instances!")

            def merge_platform_dict(source, destination):
                for platform in source:
                    destination.setdefault(platform, {}).update(source[platform])

            new_class.port_map = {}
            new_class.drivers = {}
            new_class.profiles = {}

            for base in bases:
                if not issubclass(base, DeviceBase):
                    continue

                # Merge port maps from base classes.
                merge_platform_dict(base.port_map, new_class.port_map)
                # Merge drivers from base classes.
                merge_platform_dict(base.drivers, new_class.drivers)
                # Merge profiles from base classes.
                merge_platform_dict(base.profiles, new_class.profiles)

            merge_platform_dict(attrs.get('port_map', {}), new_class.port_map)
            merge_platform_dict(attrs.get('drivers', {}), new_class.drivers)
            merge_platform_dict(attrs.get('profiles', {}), new_class.profiles)

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

        # Register a new choice in the configuration registry.
        registration.point('node.config').register_choice(
            'core.general#router',
            registration.Choice(
                cls.identifier,
                cls.get_display_name(),
                limited_to=('core.general#platform', platform.name),
                # Include some more device metadata.
                manufacturer=cls.manufacturer,
                model=cls.name,
            )
        )

        # Register a new choice for available device ports.
        for port in cls.ports:
            if isinstance(port, SwitchVLANPreset):
                continue

            registration.point('node.config').register_choice(
                'core.interfaces#eth_port',
                registration.Choice(
                    port.identifier,
                    port.description,
                    limited_to=('core.general#router', cls.identifier),
                )
            )

        # Register switches.
        for switch in cls.switches:
            # Register the switch.
            registration.point('node.config').register_choice(
                'core.switch#switch',
                registration.Choice(
                    switch.identifier,
                    '{} - {}'.format(switch.identifier, switch.description),
                    limited_to=('core.general#router', cls.identifier),
                )
            )

        # Register a new choice for available device radios.
        for radio in cls.radios:
            registration.point('node.config').register_choice(
                'core.interfaces#wifi_radio',
                registration.Choice(
                    radio.identifier,
                    radio.description,
                    limited_to=('core.general#router', cls.identifier),
                )
            )

        # Register CGM methods.
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
    def get_display_name(cls):
        """
        Returns a display name for this device.
        """

        return _("%(manufacturer)s - %(name)s") % {'manufacturer': cls.manufacturer, 'name': cls.name}

    @classmethod
    def resolve_platform_dict(cls, platform, dictionary, default=None):
        """
        Resolve platform-keyed dictionary.

        :param platform: Platform instance
        :param dictionary: Source dictionary
        :param default: Optional default value
        """

        for name in [platform.name] + platform.includes:
            if name in dictionary:
                return dictionary[name]

        return default

    @classmethod
    def get_port_map(cls, platform):
        """
        Return platform-specific port map.

        :param platform: Platform instance
        """

        return cls.resolve_platform_dict(platform, cls.port_map, {})

    @classmethod
    def get_driver(cls, platform, interface):
        """
        Return platform-specific driver for the given interface.

        :param platform: Platform instance
        :param interface: Interface name
        """

        return cls.resolve_platform_dict(platform, cls.drivers, {})[interface]

    @classmethod
    def remap_port(cls, platform, interface_or_port):
        """
        Remaps a port according to the port mapping.

        :param platform: Platform instance
        :param interface_or_port: Interface model or port identifier
        """

        from . import models as cgm_models

        if isinstance(interface_or_port, cgm_models.EthernetInterfaceConfig):
            interface_or_port = interface_or_port.eth_port
        elif isinstance(interface_or_port, cgm_models.WifiRadioDeviceConfig):
            interface_or_port = interface_or_port.wifi_radio

        # If a direct mapping exists, use it. Otherwise, check if this is a switched
        # port and if a special switch-wide mapping is available.
        mapping = cls.resolve_platform_dict(platform, cls.port_map, {}).get(interface_or_port, None)
        if mapping is not None:
            if isinstance(mapping, SwitchPortMap):
                return mapping.switch

            return mapping

        # Handle ethernet ports.
        port = cls.get_port(interface_or_port)
        if isinstance(port, tuple):
            switch, vlan = port
            switch_map = cls.resolve_platform_dict(platform, cls.port_map, {}).get(switch.identifier, None)
            if isinstance(switch_map, SwitchPortMap):
                return switch_map.get_port(vlan)

    @classmethod
    def get_vif_mapping(cls, platform, radio, vif):
        """
        Returns a name for the wireless virtual interface.

        :param platform: Platform instance
        :param radio: Radio identifier
        :param vif: Wireless virtual interface model
        """

        return ('%s%d' % (vif.mode, vif.get_index())).lower().replace(' ', '')

    @classmethod
    def get_bridge_mapping(cls, platform, bridge):
        """
        Returns a bridge name.

        :param platform: Platform instance
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

        atoms = identifier.split(SWITCH_ATOM_SEPARATOR)

        if len(atoms) == 1:
            # Simple port name.
            for port in cls.ports:
                if port.identifier == atoms[0]:
                    return port
        elif len(atoms) == 2:
            # A configured switch VLAN, we return the correct switch and parsed VLAN.
            switch, vlan = atoms
            switch = cls.get_switch(switch)
            if not switch:
                return

            return switch, switch.get_vlan_from_identifier(vlan)
        else:
            raise ValueError('Unsupported number of atoms in port identifier')


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

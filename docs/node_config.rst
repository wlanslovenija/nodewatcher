.. _registry-node-config-schema:

Node Configuration Schema
=========================

Per-node configuration schema in nodewatcher is built from various Django models and mixins,
using light extensions provided by the :ref:`registry-api`. This documentation specifies,
for each registry item identifier (see :ref:`registry-api-items`) the models that provide parts
of the final schema.

Each node is defined as an instance of :class:`nodewatcher.core.models.Node` and represents a
network-connected device that may be managed by nodewatcher. The model instance itself only provides
a universally unique identifier (UUID) and has no other attributes. All configuration attributes
are added by various models through the use of the registry.

core.general
------------

The general schema contains a basic node name configuration.

.. autoclass:: nodewatcher.core.models.GeneralConfig()

   .. note::
      There may be only one instance of this model (or subclasses) per node.

   :param name: Name of the configured node. It may be used as a hostname when
     configuring an actual device.
   :type name: string

In case firmware generation support is enabled (by loading the :mod:`nodewatcher.core.generator.cgm`
module), an extended set of options becomes available. These options configure the specific target
device and firmware version that should be generated when requested.

.. autoclass:: nodewatcher.core.generator.cgm.models.CgmGeneralConfig()
   :show-inheritance:

   :param router: Type of the configured device. Available device identifiers are automatically
     populated by the :mod:`nodewatcher.modules.devices` module. See also :ref:`cgm-devices`.
   :type router: registered choice

   :param platform: Target platform. Available platforms are populated by loading the appropriate
     applications (for example, :mod:`nodewatcher.modules.platforms.openwrt` for OpenWrt support).
     See also :ref:`cgm-platforms`.
   :type platform: registered choice

   :param build_channel: The firmware generator build channel (see :ref:`cgm-build-channel`) that
     should be used to obtain new versions of firmware images for this node. The value may be
     set to ``None`` which means that a default build channel will be used. When a build channel
     is removed, any nodes having the specified build channel set will see it reset to ``None``.
   :type build_channel: foreign key to :class:`~nodewatcher.core.generator.models.BuildChannel`

   :param version: Specific firmware version that should be built (see :ref:`cgm-build-version`).
     In most cases this should be set to ``None`` which means that a default version will be selected
     based on the selected build channel. When a firmware version is removed, any nodes having the
     specified version set will see it reset to ``None``.
   :type version: foreign key to :class:`~nodewatcher.core.generator.models.BuildVersion`

core.type
---------

The :mod:`nodewatcher.modules.administration.types` module provides a schema extension that enables
types for each node to be configured. Currently, the following node types are registered by default:

  * server,
  * wireless,
  * test,
  * mobile,
  * dead,
  * unknown.

Additional types may be registered by other modules.

.. autoclass:: nodewatcher.modules.administration.types.models.TypeConfig()

   .. note::
      There may be only one instance of this model (or subclasses) per node.

   :param type: Device type.
   :type type: registered choice

core.project
------------

The :mod:`nodewatcher.modules.administration.projects` module provides a schema extension that enables
projects for each node to be configured. Projects provide logical or geographical structuring of node
deployments.

.. autoclass:: nodewatcher.modules.administration.projects.models.Project()

   :param name: Name of the project.
   :type name: string

   :param description: Additional description of the project.
   :type description: text

   :param location: Geographical location of the project.
   :type location: geometry

   :param ip_pools: IP allocation pools that may be used by this project.
   :type ip_pools: many to many to :class:`~nodewatcher.core.allocation.ip.models.IpPool`

   :param default_ip_pool: Default IP allocation pool.
   :type default_ip_pool: foreign key to :class:`~nodewatcher.core.allocation.ip.models.IpPool`

Each project may have multiple SSID configurations attached.

.. autoclass:: nodewatcher.modules.administration.projects.models.SSID()

   :param project: Reference to project.
   :type project: foreign key to :class:`~nodewatcher.modules.administration.projects.models.Project`

   :param purpose: Specifies the usage for this SSID configuration. The exact semantics of
     this value are currently not defined.
   :type purpose: string

   :param default: Should this SSID configuration be used by default.
   :type default: bool

   :param bssid: Configured BSSID.
   :type bssid: :class:`~nodewatcher.core.registry.fields.MACAddressField`

   :param essid: Configured ESSID.
   :type essid: string

For each node a project may then be configured.

.. autoclass:: nodewatcher.modules.administration.projects.models.ProjectConfig()

   .. note::
      There may be only one instance of this model (or subclasses) per node.

   :param project: The project that this node is a part of.
   :type project: foreign key to :class:`~nodewatcher.modules.administration.projects.models.Project`

core.description
----------------

The :mod:`nodewatcher.modules.administration.description` module provides a schema extension that
enables unstructured notes and an URL to be added to any node.

.. autoclass:: nodewatcher.modules.administration.description.models.DescriptionConfig()

   .. note::
      There may be only one instance of this model (or subclasses) per node.

   :param notes: Unstructured human-readable notes.
   :type notes: text

   :param url: URL containing any node-specific details.
   :type url: url

core.location
-------------

The :mod:`nodewatcher.modules.administration.location` module provides a schema extension that provides
geographical positioning of a node.

.. autoclass:: nodewatcher.modules.administration.location.models.LocationConfig()

   .. note::
      There may be only one instance of this model (or subclasses) per node.

   :param address: Street address.
   :type address: string

   :param city: City name.
   :type city: string

   :param country: Country name.
   :type country: :class:`~django_countries.fields.CountryField`

   :param timezone: Timezone.
   :type timezone: :class:`~timezone_field.TimeZoneField`

   :param geolocation: Geographic location.
   :type geolocation: geometry point

   :param altitude: Altitude in meters.
   :type altitude: float

core.routerid
-------------

To identify nodes within the routing protocols a configuration schema is provided to configure
the router identifier of a node. Each node may have multiple router identifiers. The following
router identifier families are registered by default:

  * ipv4,
  * ipv6.

Additional families may be registered by other modules (for example MAC addresses for L2 routing
protocols).

.. autoclass:: nodewatcher.core.models.RouterIdConfig()

   :param family: Type of the router identifier.
   :type family: registered choice

   :param router_id: Router identifier.
   :type router_id: string

For IP based router identifiers, there exist two specializations. The first enables static IP
based router ID configuration.

.. autoclass:: nodewatcher.core.models.StaticIpRouterIdConfig()
  :show-inheritance:

  :param address: IP subnet of which the first IP should be used as router ID.
  :type address: :class:`~nodewatcher.core.registry.fields.IPAddressField`

The second enables allocation of router identifiers from IP pools.

.. autoclass:: nodewatcher.core.allocation.ip.models.AllocatedIpRouterIdConfig()
  :show-inheritance:

core.authentication
-------------------

There are multiple options provided for configuring user authentication on the nodes. By default,
the :mod:`nodewatcher.core.generator.cgm` module provides a base class for all authentication
mechanisms.

.. autoclass:: nodewatcher.core.generator.cgm.models.AuthenticationConfig()

A password configuration option is also provided by default.

.. autoclass:: nodewatcher.core.generator.cgm.models.PasswordAuthenticationConfig()
   :show-inheritance:

   .. note::
      There may be only one instance of this model (or subclasses) per node.

   :param password: Password for the root user.
   :type password: string

Public key authentication is provided by :mod:`nodewatcher.modules.authentication.public_key` module.
It extends the schema with the public key authentication method. Multiple authentication methods
may be configured for each node.

.. autoclass:: nodewatcher.modules.authentication.public_key.models.PublicKeyAuthenticationConfig()
   :show-inheritance:

   :param public_key: Public key in SSH-compatible encoding format.
   :type public_key: string

Public keys should be provided in a SSH-compatible encoding format, for example::

  ssh-rsa AAAAB3NzaC1yc2EAAAADA...Oipsw25uxIvkDKjAxzQ== user@host

core.roles
----------

The module :mod:`nodewatcher.modules.administration.roles` adds support for specifying roles that
a node may have. Several default roles are provided.

.. autoclass:: nodewatcher.modules.administration.roles.models.RoleConfig()

   :param roles: A list of roles the node has.
   :type roles: registered choice

The following roles are provided by default:

  * ``system`` (the node has an important system function, required for network operation),
  * ``border-router`` (the node is a border router, enabling access to external networks),
  * ``vpn-server`` (the node provides a VPN server for other nodes),
  * ``redundancy-required`` (the node requires multiple redundant links).

core.switch
-----------

When a device supports switch configurations, the switch may be configured using this registry
item. A concrete implementation is provided with the core module.

.. autoclass:: nodewatcher.core.generator.cgm.models.SwitchConfig()

    :param switch: Identifier of the switch that is being configured.
    :type switch: registered choice

    :param vlan_preset: Switch VLAN configuration preset identifier that should be used.
    :type vlan_preset: string

All switches must define a default preset under the identifier ``default`` in their device
descriptor.

core.switch.vlan
----------------

Each switch can contain multiple VLAN configurations, which define how individual switch
ports are grouped into VLANs.

.. autoclass:: nodewatcher.core.generator.cgm.models.VLANConfig()

    :param switch: Parent switch this VLAN configuration belongs to.
    :type switch: foreign key to :class:`~nodewatcher.core.generator.cgm.models.SwitchConfig`

    :param name: Name of the VLAN for easier identification.
    :type name: string

    :param vlan: VLAN identifier that is being configured.
    :type vlan: integer

    :param ports: Ports that should be grouped under the configured VLAN.
    :type ports: list of integers

core.interfaces
---------------

In order to configure network interfaces, several interface types are implemented. All interface
configurations extend a base class.

.. autoclass:: nodewatcher.core.generator.cgm.models.InterfaceConfig()

   :param enabled: True if the interface should be enabled.
   :type enabled: bool

An abstract mixin is provided for configuring interfaces which may be used for routing purposes
by the registered routing protocols. In case an interface should support routing, it should
include the mixin among its bases.

.. autoclass:: nodewatcher.core.generator.cgm.models.RoutableInterface()

   :param routing_protocols: The routing protocols that should be used over this interface. The
     value may be ``[]`` in case no routing protocol is to be used. Available routing protocols
     are populated by modules implementing their support (for example :mod:`nodewatcher.modules.routing.olsr`
     for OLSR support). Multiple protocols may be configured for an interface.
   :type routing_protocols: registered multiple choice

The following interface types are currently implemented by :mod:`nodewatcher.core.generator.cgm`:

  * ethernet,
  * wifi radio,
  * wifi virtual interface,
  * mobile,
  * vpn,
  * bridge.

.. autoclass:: nodewatcher.core.generator.cgm.models.EthernetInterfaceConfig()
   :show-inheritance:

   :param eth_port: Ethernet port that this interface is connected to. Available ethernet ports
     depend on the selected device and configured switch VLANs.
   :type eth_port: registered choice

   :param uplink: Should this interface be considered as a WAN uplink.
   :type uplink: bool

   :param mac_address: MAC address in case it should be configured to a fixed address.
   :type mac_address: :class:`~nodewatcher.core.registry.fields.MACAddressField`

Wireless interfaces are split into two configuration classes. The first class instances represent
physical wireless radios.

.. autoclass:: nodewatcher.core.generator.cgm.models.WifiRadioDeviceConfig()
   :show-inheritance:

   :param wifi_radio: The physical radio that should be used by this interface. Available
     radios depend on the selected device.
   :type wifi_radio: registered choice

   :param protocol: Wireless protocol that should be configured for this interface. Available
     protocols depend on the selected wireless radio.
   :type protocol: registered choice

   :param channel: Wireless channel. Available channels depend on the selected protocol.
   :type channel: registered choice

   :param channel_width: Wireless channel width. Available widths depend on the selected protocol.
   :type channel_width: registered choice

   :param ack_distance: ACK distance.
   :type ack_distance: int

   :param rts_threshold: RTS threshold.
   :type rts_threshold: int

   :param frag_threshold: Fragmentation threshold.
   :type frag_threshold: int

Then, for each wireless radio, multiple wireless virtual interfaces may be configured. Each virtual
interface will cause a new wireless network to be created. By default, the following wireless modes
are registered:

  * mesh,
  * ap,
  * sta.

Additional modes may be registered by other modules.

.. autoclass:: nodewatcher.core.generator.cgm.models.WifiInterfaceConfig()
   :show-inheritance:

   :param device: Reference to the parent wireless radio interface.
   :type device: foreign key to :class:`~nodewatcher.core.generator.cgm.models.WifiRadioDeviceConfig`

   :param mode: Wireless mode.
   :type mode: registered choice

   :param essid: Network ESSID.
   :type essid: string

   :param bssid: Network BSSID.
   :type bssid: :class:`~nodewatcher.core.registry.fields.MACAddressField`

Modules may provide support for VPN tunnel interfaces. The :mod:`nodewatcher.modules.vpn.tunneldigger`
module provides support for configuring Tunneldigger-based tunnels.

.. autoclass:: nodewatcher.modules.vpn.tunneldigger.models.TunneldiggerInterfaceConfig()
   :show-inheritance:

   :param mac: MAC address of the VPN interface. By default a virtual address is automatically
     generated.
   :type mac: :class:`~nodewatcher.core.registry.fields.MACAddressField`

   :param server: Reference to VPN server configuration that this interface should connect to.
   :type server: foreign key to :class:`~nodewatcher.modules.vpn.tunneldigger.models.TunneldiggerServer`

Configuration classes for mobile interfaces, like 3G, are also provided.

.. autoclass:: nodewatcher.core.generator.cgm.models.MobileInterfaceConfig()
   :show-inheritance:

   :param service: Mobile service type (eg. umts, gprs, cdma).
   :type service: registered choice

   :param device: Serial/USB device that should be used for communicating with the modem. Available
     serial devices depend on the selected router device.
   :type device: registered choice

   :param apn: APN configuration.
   :type apn: string

   :param pin: PIN configuration.
   :type pin: string

   :param username: Username.
   :type username: string

   :param password: Password.
   :type password: string

Bridges consisting of multiple other devices may also be configured.

.. autoclass:: nodewatcher.core.generator.cgm.models.BridgeInterfaceConfig()
   :show-inheritance:

   :param name: Bridge name.
   :type name: string

   :param stp: Should STP be enabled.
   :type stp: bool

   :param mac_address: MAC address in case it should be configured to a fixed address.
   :type mac_address: :class:`~nodewatcher.core.registry.fields.MACAddressField`

core.interfaces.network
-----------------------

For each of the above physical interfaces, various network configurations may be set. Note that not
all network configurations may be used on all types of interfaces. A base class is provided for all
network configurations.

.. autoclass:: nodewatcher.core.generator.cgm.models.NetworkConfig()

   :param enabled: Should this network configuration be enabled.
   :type enabled: bool

   :param interface: Parent interface that this network configuration belongs to.
   :type interface: foreign key to :class:`~nodewatcher.core.generator.cgm.models.InterfaceConfig`

   :param description: Human-readable description.
   :type description: string

An abstract mixin is provided for configuring networks which may be announce via a dynamic
routing protocol. In case a network should support such announcement, it should include the mixin
among its bases.

.. autoclass:: nodewatcher.core.generator.cgm.models.AnnouncableNetwork()

   :param routing_announces: Should this network be announced via routing protocols. Available
     choices are provided by routing protocol implementations. In case the value is ``[]``, the
     network is not announced via any routing protocol. Multiple protocols may be configured for
     a network.
   :type routing_announces: registered multiple choice

Another abstract mixin is provided for configuring networks which may be leased to clients via
DHCP or other protocols. In case a network should support leases, it should include the mixin
among its bases.

.. autoclass:: nodewatcher.core.generator.cgm.models.LeasableNetwork()

  :param lease_type: Type of network lease. In case the value is ``None``, the network will not
    be leased to any clients.
  :type lease_type: registered choice

  :param lease_duration: Duration of each lease.
  :type lease_duration: :class:`timedelta.fields.TimedeltaFields`

The simplest is a static IP network configuration.

.. autoclass:: nodewatcher.core.generator.cgm.models.StaticNetworkConfig()
   :show-inheritance:

   :param address: IP address and network mask (in CIDR notation).
   :type address: :class:`~nodewatcher.core.registry.fields.IPAddressField`

   :param gateway: Gateway address (may be ``None``).
   :type gateway: :class:`~nodewatcher.core.registry.fields.IPAddressField`

Resources may also be configured from various pools (for available fields, see :ref:`resources`).

.. autoclass:: nodewatcher.core.generator.cgm.models.AllocatedNetworkConfig()
   :show-inheritance:

Interfaces may also be configured to obtain addresses via DHCP.

.. autoclass:: nodewatcher.core.generator.cgm.models.DHCPNetworkConfig()
   :show-inheritance:

Ethernet interfaces may also be configured via PPPoE.

.. autoclass:: nodewatcher.core.generator.cgm.models.PPPoENetworkConfig()
   :show-inheritance:

   :param username: Username.
   :type username: string

   :param password: Password.
   :type password: string

For bridge slaves, network configuration specifies the master bridge interface.

.. autoclass:: nodewatcher.core.generator.cgm.models.BridgedNetworkConfig()
   :show-inheritance:

   :param bridge: Master bridge interface.
   :type bridge: foreign key to :class:`~nodewatcher.core.generator.cgm.models.BridgeInterfaceConfig`

core.interfaces.limits
----------------------

Various limits (like QoS) may also be configured for each interface.

.. autoclass:: nodewatcher.core.generator.cgm.models.InterfaceLimitConfig()

   :param enabled: Should this interface limit be enabled.
   :type enabled: bool

   :param interface: Interface that this limit applies to.
   :type interface: foreign key to :class:`~nodewatcher.core.generator.cgm.models.InterfaceConfig`

Currently, a throughput limit may be configured.

.. autoclass:: nodewatcher.core.generator.cgm.models.ThroughputInterfaceLimitConfig()
   :show-inheritance:

   :param limit_in: Inbound traffic throughput limit.
   :type limit_in: registered choice

   :param limit_out: Outbound traffic throughput limit.
   :type limit_out: registered choice

core.servers.dns
----------------

Multiple DNS servers may also be configured.

.. autoclass:: nodewatcher.core.generator.cgm.models.DnsServerConfig()

   :param address: IP address of the DNS server.
   :type address: :class:`~nodewatcher.core.registry.fields.IPAddressField`

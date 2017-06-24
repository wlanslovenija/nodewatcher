from nodewatcher.core.defaults import Name
from nodewatcher.core.generator.cgm.defaults import Device, NetworkModuleMixin
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.generator.cgm import devices as cgm_devices
from nodewatcher.core.registry import forms as registry_forms

from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.administration.projects.defaults import Project
from nodewatcher.modules.administration.types.defaults import NodeType
from nodewatcher.modules.defaults.network_profile.defaults import NetworkProfile
from nodewatcher.modules.vpn.tunneldigger import models as td_models


# TODO: Make more general and move out of extra.wlansi.
class ClearInterfaces(registry_forms.FormDefaultsModule):
    """
    Form defaults module that removes all interfaces during the configuration
    stage.
    """

    def configure(self, context, state, create):
        def filter_remove_item(item):
            # Do not remove tunneldigger interfaces as they are already handled by other
            # defaults handlers.
            if isinstance(item, td_models.TunneldiggerInterfaceConfig):
                return False

            # Remove everything else.
            return True
        state.remove_items('core.interfaces', filter=filter_remove_item)


# TODO: Make more general and move out of extra.wlansi.
class EthernetModule(NetworkModuleMixin, registry_forms.FormDefaultsModule):
    """
    Form defaults module for configuring switches and ethernet ports.
    """

    requires = [
        Device(),
        Project(),
        NodeType(),
        NetworkProfile(),
        ClearInterfaces()
    ]
    requires_context = ['routing_protocols']

    def pre_configure(self, context, state, create):
        device = context['device']

        vlan_ports = {}
        for switch in state.filter_items('core.switch', klass=cgm_models.SwitchConfig):
            switch_descriptor = device.get_switch(switch.switch)
            for vlan in state.filter_items('core.switch.vlan', klass=cgm_models.VLANConfig, parent=switch):
                vlan_ports[switch_descriptor.get_port_identifier(vlan.vlan)] = vlan

        # Compute the list of available ports.
        available_ports = [port.identifier for port in device.ports] + vlan_ports.keys()

        # Check if we can reuse the LAN port, so when there are multiple choices, the user
        # can force a specific port to be used as LAN.
        lan_port = None
        for interface in state.filter_items('core.interfaces', klass=cgm_models.EthernetInterfaceConfig):
            if interface.annotations.get('wlansi.lan', False) and interface.eth_port in available_ports:
                lan_port = interface.eth_port

        if len(available_ports) >= 1:
            # If there are multiple ethernet ports, use Wan0 for uplink.
            wan_port = device.get_port('wan0')
            if not wan_port:
                # Also check if there is a defined VLAN, containing "wan" in its name.
                for vlan_port in vlan_ports:
                    if 'wan' in vlan_ports[vlan_port].name.lower():
                        wan_port = vlan_port
                        break
                else:
                    wan_port = available_ports[0]
            else:
                wan_port = wan_port.identifier

            # The firt non-WAN port is for routing/clients.
            lan_extra_ports = []
            for port in available_ports:
                if port != wan_port:
                    if lan_port is None:
                        lan_port = port
                    elif port != lan_port:
                        lan_extra_ports.append(port)
        else:
            # Do not configure any ethernet ports.
            wan_port = None
            lan_port = None
            lan_extra_ports = []

        # Store bridge network defaults.
        clients_network_defaults = None
        for bridge in state.filter_items('core.interfaces',
                                         klass=cgm_models.BridgeInterfaceConfig,
                                         name='clients0'):
            for network in state.filter_items('core.interfaces.network',
                                              klass=cgm_models.AllocatedNetworkConfig,
                                              parent=bridge):
                clients_network_defaults = network

        context['ethernet'] = {
            'vlan_ports': vlan_ports,
            'available_ports': available_ports,
            'lan_port': lan_port,
            'wan_port': wan_port,
            'lan_extra_ports': lan_extra_ports,
            'clients_network_defaults': clients_network_defaults,
        }

    def configure(self, context, state, create):
        routing_protocols = context['routing_protocols']
        node_type = context['type']
        network_profiles = context['network_profiles']
        project = context['project']
        lan_port = context['ethernet']['lan_port']
        wan_port = context['ethernet']['wan_port']
        lan_extra_ports = context['ethernet']['lan_extra_ports']
        clients_network_defaults = context['ethernet']['clients_network_defaults']

        if node_type != 'backbone':
            # Setup uplink interface.
            if wan_port:
                if 'routing-over-wan' in network_profiles:
                    # Instead of uplink, use WAN port for routing. This means no network configuration.
                    self.setup_interface(
                        state,
                        cgm_models.EthernetInterfaceConfig,
                        eth_port=wan_port,
                        configuration={
                            'routing_protocols': routing_protocols,
                        },
                    )
                else:
                    # Configure WAN port as an uplink port which gets automatically configured via DHCP.
                    uplink_interface = self.setup_interface(
                        state,
                        cgm_models.EthernetInterfaceConfig,
                        eth_port=wan_port,
                        configuration={
                            'uplink': True,
                        },
                    )

                    self.setup_network(
                        state,
                        uplink_interface,
                        cgm_models.DHCPNetworkConfig,
                        configuration={
                            'dns': False,
                            'default_route': True,
                        },
                    )

            clients_interface = None
            if node_type != 'server':
                # Create a clients bridge.
                if 'nat-clients' in network_profiles:
                    # Configure clients for NAT.
                    clients_interface = self.setup_interface(
                        state,
                        cgm_models.BridgeInterfaceConfig,
                        name='clients0',
                    )

                    network_configuration = {
                        'description': "AP-LAN Client Access",
                        'family': 'ipv4',
                        'address': '172.21.42.1/24',
                        'lease_type': 'dhcp',
                        'lease_duration': '0:15:00',
                        'nat_type': 'snat-routed-networks',
                    }

                    if clients_network_defaults is not None:
                        network_configuration.update({
                            'lease_duration': clients_network_defaults.lease_duration,
                        })

                    self.setup_network(
                        state,
                        clients_interface,
                        cgm_models.StaticNetworkConfig,
                        configuration=network_configuration,
                    )
                else:
                    # Configure clients with an allocated network, announced to the mesh.
                    if 'no-lan-bridge' in network_profiles:
                        clients_interface = self.setup_interface(
                            state,
                            cgm_models.BridgeInterfaceConfig,
                            name='clients0',
                        )
                    else:
                        clients_interface = self.setup_interface(
                            state,
                            cgm_models.BridgeInterfaceConfig,
                            name='clients0',
                            configuration={
                                'routing_protocols': routing_protocols,
                            },
                        )

                    if clients_network_defaults is not None:
                        # Reuse some configuration from the previous clients network.
                        self.setup_network(
                            state,
                            clients_interface,
                            cgm_models.AllocatedNetworkConfig,
                            configuration={
                                'description': "AP-LAN Client Access",
                                'routing_announces': routing_protocols,
                                'family': 'ipv4',
                                'pool': getattr(clients_network_defaults, 'pool', None),
                                'prefix_length': clients_network_defaults.prefix_length,
                                'lease_type': 'dhcp',
                                'lease_duration': clients_network_defaults.lease_duration,
                            }
                        )
                    else:
                        self.setup_network(
                            state,
                            clients_interface,
                            cgm_models.AllocatedNetworkConfig,
                            configuration={
                                'description': "AP-LAN Client Access",
                                'routing_announces': routing_protocols,
                                'family': 'ipv4',
                                'pool': project.default_ip_pool,
                                'prefix_length': 28,
                                'lease_type': 'dhcp',
                                'lease_duration': '0:15:00',
                            }
                        )

                if lan_port:
                    # Setup routing/clients interface.
                    if ('no-lan-bridge' in network_profiles or not clients_interface):
                        # Use LAN port only for routing, do not bridge with clients.
                        lan_interface = self.setup_interface(
                            state,
                            cgm_models.EthernetInterfaceConfig,
                            eth_port=lan_port,
                            configuration={
                                'routing_protocols': routing_protocols,
                            },
                            annotations={
                                'wlansi.lan': True,
                            }
                        )
                    else:
                        # Bridge LAN port to clients.
                        lan_interface = self.setup_interface(
                            state,
                            cgm_models.EthernetInterfaceConfig,
                            eth_port=lan_port,
                            annotations={
                                'wlansi.lan': True,
                            }
                        )

                        self.setup_network(
                            state,
                            lan_interface,
                            cgm_models.BridgedNetworkConfig,
                            configuration={
                                'bridge': clients_interface,
                                'description': '',
                            },
                        )
        else:
            # Backbone node.
            if lan_port or wan_port:
                if 'backbone-with-uplink' in network_profiles:
                    # Configure WAN port as an uplink port which gets automatically configured via DHCP.
                    uplink_interface = self.setup_interface(
                        state,
                        cgm_models.EthernetInterfaceConfig,
                        eth_port=lan_port or wan_port,
                        configuration={
                            'uplink': True,
                        },
                    )

                    self.setup_network(
                        state,
                        uplink_interface,
                        cgm_models.DHCPNetworkConfig,
                        configuration={
                            'dns': False,
                            'default_route': True,
                        },
                    )
                else:
                    # Setup routing interface on all defined ports.
                    for eth_port in (lan_port, wan_port):
                        if eth_port:
                            self.setup_interface(
                                state,
                                cgm_models.EthernetInterfaceConfig,
                                eth_port=eth_port,
                                configuration={
                                    'routing_protocols': routing_protocols,
                                },
                            )

        # Setup additional routing interfaces on all extra ports.
        for extra_port in lan_extra_ports:
            self.setup_interface(
                state,
                cgm_models.EthernetInterfaceConfig,
                eth_port=extra_port,
                configuration={
                    'routing_protocols': routing_protocols,
                },
            )

        context.update({
            'clients_interface': clients_interface,
        })


# TODO: Make more general and move out of extra.wlansi.
class MobileUplinkModule(NetworkModuleMixin, registry_forms.FormDefaultsModule):
    """
    Form defaults module for configuring mobile uplinks.
    """

    requires = [
        NetworkProfile(),
        ClearInterfaces()
    ]

    def pre_configure(self, context, state, create):
        mobile_defaults = None
        for mobile_interface in state.filter_items('core.interfaces', klass=cgm_models.MobileInterfaceConfig):
            mobile_defaults = mobile_interface
            break

        context['mobile_defaults'] = mobile_defaults

    def configure(self, context, state, create):
        network_profiles = context['network_profiles']
        mobile_defaults = context['mobile_defaults']

        if 'mobile-uplink' in network_profiles:
            if mobile_defaults is not None:
                # Reuse some configuration form the previous mobile interface.
                self.setup_interface(
                    state,
                    cgm_models.MobileInterfaceConfig,
                    configuration={
                        'service': mobile_defaults.service,
                        'device': mobile_defaults.device,
                        'apn': mobile_defaults.apn,
                        'pin': mobile_defaults.pin,
                        'username': mobile_defaults.username,
                        'password': mobile_defaults.password,
                        'uplink': True,
                    }
                )
            else:
                # Create a new mobile interface.
                self.setup_interface(
                    state,
                    cgm_models.MobileInterfaceConfig,
                    configuration={
                        'service': 'umts',
                        'device': 'ppp0',
                        'uplink': True,
                    }
                )


# TODO: Make more general and move out of extra.wlansi.
class WirelessModule(NetworkModuleMixin, registry_forms.FormDefaultsModule):
    """
    Form defaults module for configuring wireless radios.
    """

    requires = [
        Name(),
        Device(),
        Project(),
        NodeType(),
        NetworkProfile(),
        EthernetModule(),
        ClearInterfaces(),
    ]
    requires_context = ['routing_protocols']

    def pre_configure(self, context, state, create):
        node_type = context['type']

        radio_defaults = {}
        wifi_uplink_defaults = {}
        wifi_backbone_defaults = {}
        for radio in state.filter_items('core.interfaces',
                                        klass=cgm_models.WifiRadioDeviceConfig):
            radio_defaults[radio.wifi_radio] = radio

            for wifi_interface in state.filter_items('core.interfaces',
                                                     klass=cgm_models.WifiInterfaceConfig,
                                                     parent=radio):
                if wifi_interface.uplink:
                    wifi_uplink_defaults[radio.wifi_radio] = wifi_interface
                elif node_type == 'backbone' and wifi_interface.annotations.get('wlansi.backbone', False):
                    # Copy over configuration from existing automatically generated backbone configuration.
                    wifi_backbone_defaults[radio.wifi_radio] = wifi_interface

        context.update({
            'radio_defaults': radio_defaults,
            'wifi_uplink_defaults': wifi_uplink_defaults,
            'wifi_backbone_defaults': wifi_backbone_defaults,
        })

    def configure_radio(self, context, state, create, radio):
        """
        Configure a single radio device.
        """

        routing_protocols = context['routing_protocols']
        network_profiles = context['network_profiles']
        project = context['project']
        node_type = context['type']
        radio_defaults = context['radio_defaults']
        clients_interface = context['clients_interface']

        # Per-radio defaults.
        radio_defaults = radio_defaults.get(radio.identifier, None)
        wifi_backbone_defaults = context['wifi_backbone_defaults'].get(radio.identifier, None)
        wifi_uplink_defaults = context['wifi_uplink_defaults'].get(radio.identifier, None)

        protocol = radio.protocols[0]
        if protocol.channels[0].frequency > 5000:
            # 5 GHz channels, default to channel 36.
            channel = protocol.get_channel_number(36).identifier
        else:
            # 2.4 GHz channels, default to channel 8.
            channel = protocol.get_channel_number(8).identifier

        tx_power = None
        ack_distance = None

        if radio_defaults:
            # Transfer over some settings.
            protocol = radio.get_protocol(radio_defaults.protocol)
            if not protocol:
                protocol = radio.protocols[0]

            if protocol.has_channel(radio_defaults.channel):
                channel = radio_defaults.channel

            tx_power = radio_defaults.tx_power
            ack_distance = radio_defaults.ack_distance

        wifi_radio = self.setup_interface(
            state,
            cgm_models.WifiRadioDeviceConfig,
            wifi_radio=radio.identifier,
            configuration={
                'protocol': protocol.identifier,
                'channel_width': 'ht20',
                'channel': channel,
                'antenna_connector': radio.connectors[0].identifier,
                'tx_power': tx_power,
                'ack_distance': ack_distance,
            },
        )

        def get_project_ssid(purpose, attribute='essid'):
            if attribute == 'essid' and 'hostname-essid' in network_profiles:
                return context['name']

            try:
                ssid = getattr(project.ssids.get(purpose=purpose), attribute)
            except project_models.SSID.DoesNotExist:
                try:
                    ssid = getattr(project.ssids.get(default=True), attribute)
                except project_models.SSID.DoesNotExist:
                    raise registry_forms.RegistryValidationError(
                        "Project '{}' does not have a default {} configured. "
                        "Please configure it using the administration interface.".format(
                            project.name, attribute.upper()
                        )
                    )

            return ssid

        if node_type not in ('backbone', 'server'):
            if radio.has_feature(cgm_devices.DeviceRadio.MultipleSSID) and 'no-wifi-ap' not in network_profiles:
                # If the device supports multiple SSIDs, use one in AP mode, the other in mesh mode.
                clients_wifi = self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': 'ap',
                        'essid': get_project_ssid('ap'),
                        'isolate_clients': False,
                    },
                )

                self.setup_network(
                    state,
                    clients_wifi,
                    cgm_models.BridgedNetworkConfig,
                    configuration={
                        'bridge': clients_interface,
                        'description': '',
                    },
                )

            # Create mesh interface.
            if 'no-wifi-mesh' not in network_profiles:
                self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': 'mesh',
                        'essid': get_project_ssid('mesh'),
                        'bssid': get_project_ssid('mesh', attribute='bssid'),
                        'routing_protocols': routing_protocols,
                    },
                )
        elif node_type == 'backbone':
            # If the device is of type "Backbone", create one AP/STA.
            if wifi_backbone_defaults is not None:
                mode = wifi_backbone_defaults.mode
                if mode not in ('ap', 'sta'):
                    mode = 'ap'

                self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': mode,
                        'connect_to': wifi_backbone_defaults.connect_to,
                        'essid': wifi_backbone_defaults.essid,
                        'bssid': wifi_backbone_defaults.bssid,
                        'isolate_clients': wifi_backbone_defaults.isolate_clients,
                        'routing_protocols': routing_protocols,
                    },
                )
            else:
                self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': 'ap',
                        'essid': get_project_ssid('backbone'),
                        'isolate_clients': True,
                        'routing_protocols': routing_protocols,
                    },
                    annotations={
                        'wlansi.backbone': True,
                    },
                )

        # Wireless uplink.

        if 'wifi-uplink' in network_profiles and radio.index == 0:
            # TODO: Currently we only configure uplink for the first radio. Give the user a choice.
            if wifi_uplink_defaults is not None:
                # Reuse some configuration form the previous wifi uplink interface.
                wifi_uplink_interface = self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': 'sta',
                        'connect_to': wifi_uplink_defaults.connect_to,
                        'essid': wifi_uplink_defaults.essid,
                        'bssid': wifi_uplink_defaults.bssid,
                        'uplink': True,
                    }
                )
            else:
                # Create a new wifi uplink interface.
                wifi_uplink_interface = self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': 'sta',
                        'uplink': True,
                    }
                )

            self.setup_network(
                state,
                wifi_uplink_interface,
                cgm_models.DHCPNetworkConfig,
                configuration={
                    'dns': False,
                    'default_route': True,
                },
            )

    def configure(self, context, state, create):
        """
        Configure all available radio devices.
        """

        device = context['device']

        for radio in device.radios:
            self.configure_radio(context, state, create, radio)


# TODO: Make more general and move out of extra.wlansi.
class NetworkConfiguration(registry_forms.ComplexFormDefaults):
    modules = [
        EthernetModule(),
        MobileUplinkModule(),
        WirelessModule(),
    ]

    def __init__(self, routing_protocols):
        super(NetworkConfiguration, self).__init__(
            routing_protocols=routing_protocols,
        )

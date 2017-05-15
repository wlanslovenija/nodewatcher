from django.db import models
from django.utils import crypto

from nodewatcher.core.allocation.ip import models as ip_models
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.generator.cgm import devices as cgm_devices
from nodewatcher.core.registry import forms as registry_forms, registration

from nodewatcher.modules.administration.types import models as type_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.vpn.tunneldigger import models as td_models
from nodewatcher.modules.services.dns import models as dns_models
from nodewatcher.modules.defaults.network_profile import models as network_profile_models


class NetworkConfiguration(registry_forms.FormDefaults):
    def __init__(self, routing_protocols):
        self.routing_protocols = routing_protocols

    def set_defaults(self, state, create):
        # Get device descriptor.
        general_config = state.lookup_item(cgm_models.CgmGeneralConfig)
        if not general_config or not hasattr(general_config, 'router') or not general_config.router:
            # Return if no device is selected.
            return

        device = general_config.get_device()
        if not device:
            return

        # Get configured project.
        project_config = state.lookup_item(project_models.ProjectConfig)
        try:
            if not project_config or not project_config.project:
                return
        except project_models.Project.DoesNotExist:
            return

        # Get configured node type.
        type_config = state.lookup_item(type_models.TypeConfig)
        if not type_config or not type_config.type:
            node_type = 'wireless'
        else:
            node_type = type_config.type

        # Get network profile configuration.
        network_profile_config = state.lookup_item(network_profile_models.NetworkProfileConfig)
        if not network_profile_config or not network_profile_config.profiles:
            network_profiles = []
        else:
            network_profiles = network_profile_config.profiles

        # Preserve certain network settings in order to enable a small amount of customization.
        radio_defaults = {}
        wifi_uplink_defaults = None
        wifi_backbone_defaults = None
        for radio in state.filter_items('core.interfaces', klass=cgm_models.WifiRadioDeviceConfig):
            radio_defaults[radio.wifi_radio] = radio

            for wifi_interface in state.filter_items('core.interfaces', klass=cgm_models.WifiInterfaceConfig, parent=radio):
                if wifi_interface.uplink:
                    wifi_uplink_defaults = wifi_interface
                elif node_type == 'backbone' and wifi_interface.annotations.get('wlansi.backbone', False):
                    # Copy over configuration from existing automatically generated backbone configuration.
                    wifi_backbone_defaults = wifi_interface

        clients_network_defaults = None
        for bridge in state.filter_items('core.interfaces', klass=cgm_models.BridgeInterfaceConfig, name='clients0'):
            for network in state.filter_items('core.interfaces.network', klass=cgm_models.AllocatedNetworkConfig, parent=bridge):
                clients_network_defaults = network

        mobile_defaults = None
        for mobile_interface in state.filter_items('core.interfaces', klass=cgm_models.MobileInterfaceConfig):
            mobile_defaults = mobile_interface
            break

        # Ethernet.

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

        def filter_remove_item(item):
            # Do not remove tunneldigger interfaces as they are already handled by other
            # defaults handlers.
            if isinstance(item, td_models.TunneldiggerInterfaceConfig):
                return False

            # Remove everything else.
            return True
        state.remove_items('core.interfaces', filter=filter_remove_item)

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
                            'routing_protocols': self.routing_protocols,
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
                        'lease_duration': '15min',
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
                                'routing_protocols': self.routing_protocols,
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
                                'routing_announces': self.routing_protocols,
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
                                'routing_announces': self.routing_protocols,
                                'family': 'ipv4',
                                'pool': project_config.project.default_ip_pool,
                                'prefix_length': 28,
                                'lease_type': 'dhcp',
                                'lease_duration': '15min',
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
                                'routing_protocols': self.routing_protocols,
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
                                    'routing_protocols': self.routing_protocols,
                                },
                            )

        # Setup additional routing interfaces on all extra ports.
        for extra_port in lan_extra_ports:
            self.setup_interface(
                state,
                cgm_models.EthernetInterfaceConfig,
                eth_port=extra_port,
                configuration={
                    'routing_protocols': self.routing_protocols,
                },
            )

        # Mobile uplink.

        if 'mobile-uplink' in network_profiles:
            if mobile_defaults is not None:
                # Reuse some configuration form the previous mobile interface.
                mobile_interface = self.setup_interface(
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
                mobile_interface = self.setup_interface(
                    state,
                    cgm_models.MobileInterfaceConfig,
                    configuration={
                        'service': 'umts',
                        'device': 'ppp0',
                        'uplink': True,
                    }
                )

        # Wireless.

        try:
            radio = device.radios[0]
        except IndexError:
            return

        radio_defaults = radio_defaults.get(radio.identifier, None)

        protocol = radio.protocols[0]
        channel = protocol.channels[7].identifier
        tx_power = None
        ack_distance = None

        if radio_defaults:
            # Transfer over some settings.
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

        def get_project_ssid(purpose, default=None, attribute='essid'):
            if attribute == 'essid' and 'hostname-essid' in network_profiles:
                return general_config.name

            try:
                ssid = getattr(project_config.project.ssids.get(purpose=purpose), attribute)
            except project_models.SSID.DoesNotExist:
                try:
                    ssid = getattr(project_config.project.ssids.get(default=True), attribute)
                except project_models.SSID.DoesNotExist:
                    ssid = default

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
                        'essid': get_project_ssid('ap', 'open.wlan-si.net'),
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
                        'essid': get_project_ssid('mesh', 'mesh.wlan-si.net'),
                        'bssid': get_project_ssid('mesh', '02:CA:FF:EE:BA:BE', attribute='bssid'),
                        'routing_protocols': self.routing_protocols,
                    },
                )
        elif node_type == 'backbone':
            # If the device is of type "Backbone", create one AP/STA.
            if wifi_backbone_defaults is not None:
                mode = wifi_backbone_defaults.mode
                if mode not in ('ap', 'sta'):
                    mode = 'ap'

                backbone_wifi = self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': mode,
                        'connect_to': wifi_backbone_defaults.connect_to,
                        'essid': wifi_backbone_defaults.essid,
                        'bssid': wifi_backbone_defaults.bssid,
                        'isolate_clients': wifi_backbone_defaults.isolate_clients,
                        'routing_protocols': self.routing_protocols,
                    },
                )
            else:
                backbone_wifi = self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': 'ap',
                        'essid': get_project_ssid('backbone', 'backbone.wlan-si.net'),
                        'isolate_clients': True,
                        'routing_protocols': self.routing_protocols,
                    },
                    annotations={
                        'wlansi.backbone': True,
                    },
                )

        # Wireless uplink.

        if 'wifi-uplink' in network_profiles:
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

    def setup_item(self, state, registry_id, klass, configuration=None, annotations=None, **filter):
        # Create a new item.
        if configuration is None:
            configuration = {}

        filter.update(configuration)
        return state.append_item(klass, annotations=annotations, **filter)

    def setup_interface(self, state, klass, configuration=None, annotations=None, **filter):
        return self.setup_item(state, 'core.interfaces', klass, configuration, annotations, **filter)

    def setup_network(self, state, interface, klass, configuration=None, annotations=None, **filter):
        return self.setup_item(state, 'core.interfaces.network', klass, configuration, annotations, parent=interface, **filter)

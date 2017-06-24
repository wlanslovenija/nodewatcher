from nodewatcher.core.generator.cgm.defaults import Device, NetworkModuleMixin
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import forms as registry_forms

from nodewatcher.modules.administration.projects.defaults import Project
from nodewatcher.modules.administration.types.defaults import NodeType

from .base import ClearInterfaces, NetworkProfile


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

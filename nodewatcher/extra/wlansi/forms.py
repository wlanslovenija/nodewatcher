from django.db import models

from nodewatcher.core.allocation.ip import models as ip_models
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.generator.cgm import devices as cgm_devices
from nodewatcher.core.registry import forms as registry_forms, registration

from nodewatcher.modules.administration.types import models as type_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.vpn.tunneldigger import models as td_models
from nodewatcher.modules.services.dns import models as dns_models
from nodewatcher.modules.defaults.network_profile import models as network_profile_models


class DefaultPlatform(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Choose a default platform.
        general_config = state.lookup_item(cgm_models.CgmGeneralConfig)
        if not general_config:
            state.append_item(cgm_models.CgmGeneralConfig, platform='openwrt')
        elif not general_config.platform:
            state.update_item(general_config, platform='openwrt')

registration.point('node.config').add_form_defaults(DefaultPlatform())


class DefaultType(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Choose a default type.
        type_config = state.lookup_item(type_models.TypeConfig)
        if not type_config:
            state.append_item(type_models.TypeConfig, type='wireless')
        elif not type_config.type:
            state.update_item(type_config, type='wireless')

registration.point('node.config').add_form_defaults(DefaultType())


class DefaultProject(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Default to project 'Slovenia' in case it exists.
        try:
            slovenia_project = project_models.Project.objects.get(name='Slovenija')
        except project_models.Project.DoesNotExist:
            return

        # Choose a default project.
        project_config = state.lookup_item(project_models.ProjectConfig)
        if not project_config:
            state.append_item(project_models.ProjectConfig, project=slovenia_project)
        else:
            try:
                if project_config.project:
                    return
            except project_models.Project.DoesNotExist:
                state.update_item(project_config, project=slovenia_project)

registration.point('node.config').add_form_defaults(DefaultProject())


class DefaultRouterID(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Ensure there is one router ID allocated from the default pool.
        router_ids = state.filter_items('core.routerid')

        # Check if we have a project selected.
        project_config = state.lookup_item(project_models.ProjectConfig)
        try:
            if not project_config or not project_config.project:
                return
        except project_models.Project.DoesNotExist:
            return

        # Create a new allocated router identifier from the default IP pool.
        if router_ids:
            state.update_item(
                router_ids[0],
                family='ipv4',
                pool=project_config.project.default_ip_pool,
                prefix_length=29,
            )
        else:
            state.append_item(
                ip_models.AllocatedIpRouterIdConfig,
                family='ipv4',
                pool=project_config.project.default_ip_pool,
                prefix_length=29,
            )

registration.point('node.config').add_form_defaults(DefaultRouterID())


class NetworkConfiguration(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # Get device descriptor.
        general_config = state.lookup_item(cgm_models.CgmGeneralConfig)
        if not general_config or not general_config.router:
            # Return if no device is selected.
            return

        device = general_config.get_device()

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
        for radio in state.filter_items('core.interfaces', klass=cgm_models.WifiRadioDeviceConfig):
            radio_defaults[radio.wifi_radio] = radio

        clients_network = None
        for bridge in state.filter_items('core.interfaces', klass=cgm_models.BridgeInterfaceConfig, name='clients0'):
            for network in state.filter_items('core.interfaces.network', klass=cgm_models.AllocatedNetworkConfig, parent=bridge):
                clients_network = network

        state.remove_items('core.interfaces')

        # Ethernet.

        if len(device.ports) >= 1:
            # If there are multiple ethernet ports, use Wan0 for uplink.
            wan_port = device.get_port('wan0')
            if not wan_port:
                wan_port = device.ports[0]

            wan_port = wan_port.identifier

            # The firt non-WAN port is for routing/clients.
            lan_port = None
            for port in device.ports:
                if port.identifier != wan_port:
                    lan_port = port.identifier
                    break
        else:
            # Do not configure any ethernet ports.
            wan_port = None
            lan_port = None

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
                            'routing_protocols': ['olsr', 'babel'],
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
                    )

            if node_type != 'server':
                # Create a clients bridge.
                if 'nat-clients' in network_profiles:
                    # Configure clients for NAT.
                    clients_interface = self.setup_interface(
                        state,
                        cgm_models.BridgeInterfaceConfig,
                        name='clients0',
                    )

                    self.setup_network(
                        state,
                        clients_interface,
                        cgm_models.StaticNetworkConfig,
                        configuration={
                            'description': "AP-LAN Client Access",
                            'family': 'ipv4',
                            'address': '172.21.42.1/24',
                            'lease_type': 'dhcp',
                            'lease_duration': '15min',
                            'nat_type': 'snat-routed-networks',
                        }
                    )
                else:
                    # Configure clients with an allocated network, announced to the mesh.
                    clients_interface = self.setup_interface(
                        state,
                        cgm_models.BridgeInterfaceConfig,
                        name='clients0',
                        configuration={
                            'routing_protocols': ['olsr', 'babel'],
                        },
                    )

                    if clients_network is not None:
                        # Reuse some configuration from the previous clients network.
                        self.setup_network(
                            state,
                            clients_interface,
                            cgm_models.AllocatedNetworkConfig,
                            configuration={
                                'description': "AP-LAN Client Access",
                                'routing_announces': ['olsr', 'babel'],
                                'family': 'ipv4',
                                'pool': clients_network.pool,
                                'prefix_length': clients_network.prefix_length,
                                'lease_type': 'dhcp',
                                'lease_duration': '15min',
                            }
                        )
                    else:
                        self.setup_network(
                            state,
                            clients_interface,
                            cgm_models.AllocatedNetworkConfig,
                            configuration={
                                'description': "AP-LAN Client Access",
                                'routing_announces': ['olsr', 'babel'],
                                'family': 'ipv4',
                                'pool': project_config.project.default_ip_pool,
                                'prefix_length': 28,
                                'lease_type': 'dhcp',
                                'lease_duration': '15min',
                            }
                        )

                if lan_port:
                    # Setup routing/clients interface.
                    lan_interface = self.setup_interface(
                        state,
                        cgm_models.EthernetInterfaceConfig,
                        eth_port=lan_port,
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
            # Setup routing interface for backbone nodes.
            if lan_port:
                lan_interface = self.setup_interface(
                    state,
                    cgm_models.EthernetInterfaceConfig,
                    eth_port=lan_port,
                    configuration={
                        'routing_protocols': ['olsr', 'babel'],
                    },
                )

        # Wireless.

        radio = device.get_radio('wifi0')
        radio_defaults = radio_defaults.get('wifi0', None)

        if not radio:
            return

        protocol = radio.protocols[0]
        channel = protocol.channels[0].identifier
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
            try:
                ssid = getattr(project_config.project.ssids.get(purpose=purpose), attribute)
            except project_models.SSID.DoesNotExist:
                try:
                    ssid = getattr(project_config.project.ssids.get(default=True), attribute)
                except project_models.SSID.DoesNotExist:
                    ssid = default

            return ssid

        if node_type != 'backbone':
            if radio.has_feature(cgm_devices.DeviceRadio.MultipleSSID):
                # If the device supports multiple SSIDs, use one in AP mode, the other in mesh mode.
                clients_wifi = self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        'mode': 'ap',
                        'essid': get_project_ssid('ap', 'open.wlan-si.net'),
                    },
                )

                clients_wifi_network = self.setup_network(
                    state,
                    clients_wifi,
                    cgm_models.BridgedNetworkConfig,
                    configuration={
                        'bridge': clients_interface,
                        'description': '',
                    },
                )

            # Create mesh interface.
            mesh_wifi = self.setup_interface(
                state,
                cgm_models.WifiInterfaceConfig,
                parent=wifi_radio,
                configuration={
                    'mode': 'mesh',
                    'essid': get_project_ssid('mesh', 'mesh.wlan-si.net'),
                    'bssid': get_project_ssid('mesh', '02:CA:FF:EE:BA:BE', attribute='bssid'),
                    'routing_protocols': ['olsr', 'babel'],
                },
            )
        else:
            # If the device is of type "Backbone", create one in AP mode.
            backbone_wifi = self.setup_interface(
                state,
                cgm_models.WifiInterfaceConfig,
                parent=wifi_radio,
                configuration={
                    'mode': 'ap',
                    'essid': get_project_ssid('backbone', 'backbone.wlan-si.net'),
                    'routing_protocols': ['olsr', 'babel'],
                },
            )

    def setup_item(self, state, registry_id, klass, configuration=None, **filter):
        # Create a new item.
        if configuration is None:
            configuration = {}

        filter.update(configuration)
        return state.append_item(klass, **filter)

    def setup_interface(self, state, klass, configuration=None, **filter):
        return self.setup_item(state, 'core.interfaces', klass, configuration, **filter)

    def setup_network(self, state, interface, klass, configuration=None, **filter):
        return self.setup_item(state, 'core.interfaces.network', klass, configuration, parent=interface, **filter)

registration.point('node.config').add_form_defaults(NetworkConfiguration())


class STAChannelAutoselect(registry_forms.FormDefaults):
    """
    Configures any radios containing VIFs in STA mode to have automatic
    channel selection.
    """

    def set_defaults(self, state, create):
        # Iterate over all configured radios and VIFs.
        for radio in state.filter_items('core.interfaces', klass=cgm_models.WifiRadioDeviceConfig):
            # TODO: Improve this filtering.
            for vif in state.filter_items('core.interfaces', klass=cgm_models.WifiInterfaceConfig, parent=radio):
                if vif.mode != 'sta':
                    continue

                # Ensure that the parent radio has the channel set to auto.
                state.update_item(vif.device, channel='')

registration.point('node.config').add_form_defaults(STAChannelAutoselect())


class TunneldiggerServersOnUplink(registry_forms.FormDefaults):
    """
    Automatically configures default tunneldigger servers as soon as an
    uplink interface is configured.
    """

    def set_defaults(self, state, create):
        # Check if there are any uplink interfaces.
        if state.filter_items('core.interfaces', uplink=True):
            self.update_tunneldigger(state)
        else:
            self.remove_tunneldigger(state)

    def get_servers(self, state):
        # Get the currently configured project.
        try:
            project_config = state.filter_items('core.project')[0]
        except IndexError:
            project_config = None

        query = models.Q(PerProjectTunneldiggerServer___project=None)
        if project_config:
            query |= models.Q(PerProjectTunneldiggerServer___project=project_config.project)

        return td_models.TunneldiggerServer.objects.filter(query)

    def remove_tunneldigger(self, state):
        # Remove any tunneldigger interfaces.
        state.remove_items('core.interfaces', klass=td_models.TunneldiggerInterfaceConfig)

    def update_tunneldigger(self, state):
        # Check if there are existing tunneldigger interfaces.
        existing_ifaces = state.filter_items('core.interfaces', klass=td_models.TunneldiggerInterfaceConfig)
        configured = self.get_servers(state)

        # Update existing interfaces.
        for index, server in enumerate(configured):
            if index >= len(existing_ifaces):
                # We need to create a new interface.
                td_iface = state.append_item(
                    td_models.TunneldiggerInterfaceConfig,
                    server=server,
                    routing_protocols=['olsr', 'babel'],
                )
            else:
                # Update server configuration for an existing element.
                state.update_item(
                    existing_ifaces[index],
                    server=server,
                    routing_protocols=['olsr', 'babel'],
                )

        delta = len(existing_ifaces) - len(configured)
        if delta > 0:
            # Remove the last few interfaces.
            for td_iface in existing_ifaces[-delta:]:
                state.remove_item(td_iface)

registration.point('node.config').add_form_defaults(TunneldiggerServersOnUplink())


class DnsServers(registry_forms.FormDefaults):
    """
    Automatically configures DNS servers.
    """

    def set_defaults(self, state, create):
        # Get the DNS servers that should be configured on the current node.
        existing_servers = state.filter_items('core.servers.dns', klass=dns_models.DnsServerConfig)
        configured = self.get_servers(state)

        # Update existing servers.
        for index, server in enumerate(configured):
            if index >= len(existing_servers):
                # We need to create a new server.
                state.append_item(dns_models.DnsServerConfig, server=server)
            else:
                # Update server configuration for an existing element.
                state.update_item(existing_servers[index], server=server)

        delta = len(existing_servers) - len(configured)
        if delta > 0:
            # Remove the last few servers.
            for server in existing_servers[-delta:]:
                state.remove_item(server)

    def get_servers(self, state):
        # Get the currently configured project.
        try:
            project_config = state.filter_items('core.project')[0]
        except IndexError:
            project_config = None

        query = models.Q(PerProjectDnsServer___project=None)
        if project_config:
            query |= models.Q(PerProjectDnsServer___project=project_config.project)

        return dns_models.DnsServer.objects.filter(query)

registration.point('node.config').add_form_defaults(DnsServers())

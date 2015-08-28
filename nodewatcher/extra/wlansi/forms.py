from django.db import models

from nodewatcher.core.allocation.ip import models as ip_models
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.generator.cgm import devices as cgm_devices
from nodewatcher.core.registry import forms as registry_forms, registration

from nodewatcher.modules.administration.types import models as type_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.vpn.tunneldigger import models as td_models
from nodewatcher.modules.services.dns import models as dns_models


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

        # TODO: Make it so that we don't always remove everything.
        state.remove_items('core.interfaces')

        # Ethernet.

        if len(device.ports) > 1:
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
        elif len(device.ports) == 1:
            # If there is only one ethernet port, use it for routing/clients.
            wan_port = None
            lan_port = device.ports[0].identifier
        else:
            # Do not configure any ethernet ports.
            wan_port = None
            lan_port = None

        if node_type != 'backbone':
            # Setup uplink interface.
            if wan_port:
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

            # Create a clients bridge.
            clients_interface = self.setup_interface(
                state,
                cgm_models.BridgeInterfaceConfig,
                name='clients0',
                configuration={
                    'routing_protocols': ['olsr', 'babel'],
                },
            )

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
                    'lease_duration': '1h',
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
        protocol = radio.protocols[0]

        if not radio:
            return

        wifi_radio = self.setup_interface(
            state,
            cgm_models.WifiRadioDeviceConfig,
            wifi_radio=radio.identifier,
            configuration={
                'protocol': protocol.identifier,
                'channel_width': 'ht20',
                'channel': protocol.channels[0].identifier,
                'antenna_connector': radio.connectors[0].identifier,
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
            project = state.filter_items('core.project')[0]
        except IndexError:
            project = None

        query = models.Q(PerProjectTunneldiggerServer___project=None)
        if project:
            query |= models.Q(PerProjectTunneldiggerServer___project=project)

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
            project = state.filter_items('core.project')[0]
        except IndexError:
            project = None

        query = models.Q(PerProjectDnsServer___project=None)
        if project:
            query |= models.Q(PerProjectDnsServer___project=project)

        return dns_models.DnsServer.objects.filter(query)

registration.point('node.config').add_form_defaults(DnsServers())

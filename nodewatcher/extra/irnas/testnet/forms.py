from django.db import models
from django.utils import crypto

from nodewatcher.core.allocation.ip import models as ip_models
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import forms as registry_forms, registration

from nodewatcher.modules.administration.types import models as type_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.monitor.sources.http import models as http_models
from nodewatcher.modules.services.dns import models as dns_models

DEFAULT_PLATFORM = 'lede'
DEFAULT_NODE_TYPE = 'wireless'


class DefaultPlatform(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Choose a default platform.
        general_config = state.lookup_item(cgm_models.CgmGeneralConfig)
        if not general_config:
            state.append_item(cgm_models.CgmGeneralConfig, platform=DEFAULT_PLATFORM)
        elif not general_config.platform:
            state.update_item(general_config, platform=DEFAULT_PLATFORM)

registration.point('node.config').add_form_defaults(DefaultPlatform())


class DefaultType(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Choose a default type.
        type_config = state.lookup_item(type_models.TypeConfig)
        if not type_config:
            state.append_item(type_models.TypeConfig, type=DEFAULT_NODE_TYPE)
        elif not type_config.type:
            state.update_item(type_config, type=DEFAULT_NODE_TYPE)

registration.point('node.config').add_form_defaults(DefaultType())


class DefaultProject(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Default to project 'TestNet' in case it exists.
        try:
            testnet_project = project_models.Project.objects.get(name='TestNet')
        except project_models.Project.DoesNotExist:
            return

        # Choose a default project.
        project_config = state.lookup_item(project_models.ProjectConfig)
        if not project_config:
            state.append_item(project_models.ProjectConfig, project=testnet_project)
        else:
            try:
                if project_config.project:
                    return
            except project_models.Project.DoesNotExist:
                state.update_item(project_config, project=testnet_project)

registration.point('node.config').add_form_defaults(DefaultProject())


class DefaultTelemetrySource(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        telemetry_config = state.lookup_item(http_models.HttpTelemetrySourceConfig)
        if not telemetry_config:
            state.append_item(http_models.HttpTelemetrySourceConfig, source='push')
        else:
            state.update_item(telemetry_config, source='push')

registration.point('node.config').add_form_defaults(DefaultTelemetrySource())


class DefaultPassword(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Generate a default random password in case no authentication is configured.
        try:
            state.filter_items('core.authentication')[0]
        except IndexError:
            state.append_item(
                cgm_models.PasswordAuthenticationConfig,
                password=crypto.get_random_string(),
            )

registration.point('node.config').add_form_defaults(DefaultPassword())


class DefaultRouterID(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Ensure there is one router ID allocated from the default pool.
        router_ids = state.filter_items('core.routerid')
        if router_ids:
            return

        # Check if we have a project selected.
        project_config = state.lookup_item(project_models.ProjectConfig)
        try:
            if not project_config or not project_config.project:
                return
        except project_models.Project.DoesNotExist:
            return

        # Create a new allocated router identifier from the default IP pool.
        state.append_item(
            ip_models.AllocatedIpRouterIdConfig,
            family='ipv4',
            pool=project_config.project.default_ip_pool,
            prefix_length=28,
        )

registration.point('node.config').add_form_defaults(DefaultRouterID())


class NetworkConfiguration(registry_forms.FormDefaults):
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
            node_type = DEFAULT_NODE_TYPE
        else:
            node_type = type_config.type

        # Preserve certain network settings in order to enable a small amount of customization.
        radio_defaults = {}
        wifi_backbone_defaults = None
        for radio in state.filter_items('core.interfaces', klass=cgm_models.WifiRadioDeviceConfig):
            radio_defaults[radio.wifi_radio] = radio

            for wifi_interface in state.filter_items('core.interfaces', klass=cgm_models.WifiInterfaceConfig, parent=radio):
                if node_type == 'wireless' and wifi_interface.annotations.get('testnet.wireless', False):
                    # Copy over configuration from existing automatically generated wireless configuration.
                    wifi_backbone_defaults = wifi_interface

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
            if interface.annotations.get('testnet.lan', False) and interface.eth_port in available_ports:
                lan_port = interface.eth_port

        state.remove_items('core.interfaces')

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

        if node_type == 'gw':
            # Setup uplink interface.
            if wan_port:
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

            # TODO: Announce default route.

            # Setup routing interface on LAN port.
            lan_extra_ports.append(lan_port)
        elif node_type in ('backbone', 'wireless'):
            # Setup routing interface on all defined ports.
            for eth_port in (lan_port, wan_port):
                if eth_port:
                    self.setup_interface(
                        state,
                        cgm_models.EthernetInterfaceConfig,
                        eth_port=eth_port,
                        configuration={
                            'routing_protocols': ['babel'],
                        },
                    )

        # Setup additional routing interfaces on all extra ports.
        for extra_port in lan_extra_ports:
            self.setup_interface(
                state,
                cgm_models.EthernetInterfaceConfig,
                eth_port=extra_port,
                configuration={
                    'routing_protocols': ['babel'],
                },
            )

        # Wireless.

        if node_type != 'wireless':
            return

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
            try:
                ssid = getattr(project_config.project.ssids.get(purpose=purpose), attribute)
            except project_models.SSID.DoesNotExist:
                try:
                    ssid = getattr(project_config.project.ssids.get(default=True), attribute)
                except project_models.SSID.DoesNotExist:
                    ssid = default

            return ssid

        # Create one AP/STA.
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
                    'routing_protocols': ['babel'],
                },
            )
        else:
            self.setup_interface(
                state,
                cgm_models.WifiInterfaceConfig,
                parent=wifi_radio,
                configuration={
                    'mode': 'ap',
                    'essid': get_project_ssid('backbone', 'backbone.testnet'),
                    'isolate_clients': True,
                    'routing_protocols': ['babel'],
                },
                annotations={
                    'wlansi.backbone': True,
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

registration.point('node.config').add_form_defaults(NetworkConfiguration())


class STAChannelAutoselect(registry_forms.FormDefaults):
    """
    Configures any radios containing VIFs in STA mode to have automatic
    channel selection.
    """

    def set_defaults(self, state, create):
        # Iterate over all configured radios and VIFs.
        for radio in state.filter_items('core.interfaces', klass=cgm_models.WifiRadioDeviceConfig):
            all_vifs_sta = None
            for vif in state.filter_items('core.interfaces', klass=cgm_models.WifiInterfaceConfig, parent=radio):
                if all_vifs_sta is None and vif.mode == 'sta':
                    all_vifs_sta = True
                elif vif.mode != 'sta':
                    all_vifs_sta = False

            if all_vifs_sta:
                # Ensure that the parent radio has the channel set to auto.
                state.update_item(radio, channel='')

registration.point('node.config').add_form_defaults(STAChannelAutoselect())


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
        # Get configured project.
        project_config = state.lookup_item(project_models.ProjectConfig)
        try:
            if project_config and not project_config.project:
                project_config = None
        except project_models.Project.DoesNotExist:
            project_config = None

        query = models.Q(PerProjectDnsServer___project=None)
        if project_config:
            query |= models.Q(PerProjectDnsServer___project=project_config.project)

        return dns_models.DnsServer.objects.filter(query)

registration.point('node.config').add_form_defaults(DnsServers())

from nodewatcher.core.defaults import Name
from nodewatcher.core.generator.cgm.defaults import Device, NetworkModuleMixin
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.generator.cgm import devices as cgm_devices
from nodewatcher.core.registry import forms as registry_forms

from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.administration.projects.defaults import Project
from nodewatcher.modules.administration.types.defaults import NodeType

from .base import ClearInterfaces, NetworkProfile
from .ethernet import EthernetModule


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
        wireless_mesh_type = context['wireless_mesh_type']
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
            if wireless_mesh_type is not None:
                self.setup_interface(
                    state,
                    cgm_models.WifiInterfaceConfig,
                    parent=wifi_radio,
                    configuration={
                        # Use 802.11s if checked, otherwise use ad-hoc.
                        'mode': 'mesh11s' if wireless_mesh_type == '80211s' else 'mesh',
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
            # Do not configure USB radios automatically as they may not even be there.
            if isinstance(radio, cgm_devices.USBRadio):
                continue

            self.configure_radio(context, state, create, radio)

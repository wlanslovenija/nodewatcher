from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.generator.cgm import devices as cgm_devices
from nodewatcher.core.registry import forms as registry_forms, registration

from nodewatcher.modules.administration.types import models as type_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.monitor.sources.http import models as http_models

from . import models as commotion_models


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

        # Default to project 'Commotion' in case it exists.
        try:
            commotion_project = project_models.Project.objects.get(name='Commotion')
        except project_models.Project.DoesNotExist:
            return

        # Choose a default project.
        project_config = state.lookup_item(project_models.ProjectConfig)
        if not project_config:
            state.append_item(project_models.ProjectConfig, project=commotion_project)
        else:
            try:
                if project_config.project:
                    return
            except project_models.Project.DoesNotExist:
                state.update_item(project_config, project=commotion_project)

registration.point('node.config').add_form_defaults(DefaultProject())


class DefaultTelemetrySource(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        telemetry_config = state.lookup_item(http_models.HttpTelemetrySourceConfig)
        if not telemetry_config:
            state.append_item(http_models.HttpTelemetrySourceConfig, source='push')
        else:
            state.update_item(telemetry_config, source='push')

registration.point('node.config').add_form_defaults(DefaultTelemetrySource())


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
                commotion_models.CommotionNetworkConfig,
                configuration={
                    'network_class': 'wired',
                    'dhcp': 'client',
                }
            )

        # Create a clients bridge.
        clients_interface = self.setup_interface(
            state,
            cgm_models.BridgeInterfaceConfig,
            name='clients',
        )

        self.setup_network(
            state,
            clients_interface,
            commotion_models.CommotionNetworkConfig,
            configuration={
                'network_class': 'client',
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

        # Currently wireless is not configured by default.

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

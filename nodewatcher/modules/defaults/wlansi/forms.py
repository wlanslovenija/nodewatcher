from django.db import models

from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import forms as registry_forms, registration

from nodewatcher.modules.vpn.tunneldigger import models as td_models


class STAChannelAutoselect(registry_forms.FormDefaults):
    """
    Configures any radios containing VIFs in STA mode to have automatic
    channel selection.
    """

    def set_defaults(self, state):
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

    def set_defaults(self, state):
        # Check if there are any uplink interfaces.
        if state.filter_items('core.interfaces', uplink=True):
            self.update_tunneldigger(state)
        else:
            self.remove_tunneldigger(state)

    def get_servers(self, state):
        # Get the currently configured project.
        project = state.filter_items('core.project')[0]

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

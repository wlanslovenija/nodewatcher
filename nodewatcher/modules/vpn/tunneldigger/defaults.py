from django.apps import apps

from nodewatcher.core.registry import forms as registry_forms

from . import models

if apps.is_installed('nodewatcher.modules.administration.projects'):
    from nodewatcher.modules.administration.projects import models as project_models


class TunneldiggerServersOnUplink(registry_forms.FormDefaults):
    """
    Automatically configures default tunneldigger servers as soon as an
    uplink interface is configured.
    """

    def __init__(self, routing_protocols):
        self.routing_protocols = routing_protocols

    def set_defaults(self, state, create):
        # Check if there are any uplink interfaces.
        if state.filter_items('core.interfaces', uplink=True):
            self.update_tunneldigger(state)
        else:
            self.remove_tunneldigger(state)

    def get_servers(self, state):
        # Handle per-project configuration when available.
        if apps.is_installed('nodewatcher.modules.administration.projects'):
            # Get configured project.
            project_config = state.lookup_item(project_models.ProjectConfig)
            try:
                if project_config and not project_config.project:
                    project_config = None
            except project_models.Project.DoesNotExist:
                project_config = None

            if project_config:
                # Check if there are any project-specific servers configured. In this
                # case, we only use those, otherwise we use the default ones.
                qs = models.TunneldiggerServer.objects.filter(
                    PerProjectTunneldiggerServer___project=project_config.project,
                    enabled=True,
                )

                if qs.exists():
                    return qs

            return models.TunneldiggerServer.objects.filter(
                PerProjectTunneldiggerServer___project=None,
                enabled=True,
            )

        return models.TunneldiggerServer.objects.filter(enabled=True)

    def remove_tunneldigger(self, state):
        # Remove any tunneldigger interfaces.
        state.remove_items('core.interfaces', klass=models.TunneldiggerInterfaceConfig)

    def update_tunneldigger(self, state):
        # Check if there are existing tunneldigger interfaces.
        existing_ifaces = state.filter_items('core.interfaces', klass=models.TunneldiggerInterfaceConfig)
        configured = self.get_servers(state)

        # Update existing interfaces.
        for index, server in enumerate(configured):
            if index >= len(existing_ifaces):
                # We need to create a new interface.
                td_iface = state.append_item(
                    models.TunneldiggerInterfaceConfig,
                    server=server,
                    routing_protocols=self.routing_protocols,
                )
            else:
                # Update server configuration for an existing element.
                state.update_item(
                    existing_ifaces[index],
                    server=server,
                    routing_protocols=self.routing_protocols,
                )

        delta = len(existing_ifaces) - len(configured)
        if delta > 0:
            # Remove the last few interfaces.
            for td_iface in existing_ifaces[-delta:]:
                state.remove_item(td_iface)

from django.apps import apps
from django.db import models

from nodewatcher.core.registry import forms as registry_forms

from . import models as dns_models

if apps.is_installed('nodewatcher.modules.administration.projects'):
    from nodewatcher.modules.administration.projects import models as project_models


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
        project_config = None

        # Handle per-project configuration when available.
        if apps.is_installed('nodewatcher.modules.administration.projects'):
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
        else:
            query = models.Q()

        return dns_models.DnsServer.objects.filter(query)

from nodewatcher.core.allocation.ip import models as ip_models
from nodewatcher.core.registry import forms as registry_forms

from . import models


class DefaultProject(registry_forms.FormDefaults):
    """
    Default project configuration.
    """

    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Choose a default project.
        default_project = models.project_default(state.get_request())

        project_config = state.lookup_item(models.ProjectConfig)
        if not project_config:
            state.append_item(models.ProjectConfig, project=default_project)
        else:
            try:
                if project_config.project:
                    return
            except models.Project.DoesNotExist:
                state.update_item(project_config, project=default_project)


class DefaultProjectRouterID(registry_forms.FormDefaults):
    """
    Default per-project router identifier.
    """

    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Ensure there is one router ID allocated from the default pool.
        router_ids = state.filter_items('core.routerid')
        if router_ids:
            return

        # Check if we have a project selected.
        project_config = state.lookup_item(models.ProjectConfig)
        try:
            if not project_config or not project_config.project:
                return
        except models.Project.DoesNotExist:
            return

        # Create a new allocated router identifier from the default IP pool.
        state.append_item(
            ip_models.AllocatedIpRouterIdConfig,
            family='ipv4',
            pool=project_config.project.default_ip_pool,
            prefix_length=29,
        )


class Project(registry_forms.FormDefaultsModule):
    """
    Form defaults module that stores node's project into the module context.

    Exported context properties:
    - ``project`` contains the ``Project`` instance
    """

    def pre_configure(self, context, state, create):
        """
        Get project for the node that is being edited.
        """

        project_config = state.lookup_item(models.ProjectConfig)
        try:
            if not project_config or not project_config.project:
                raise registry_forms.StopDefaults
        except models.Project.DoesNotExist:
            raise registry_forms.StopDefaults

        context['project'] = project_config.project

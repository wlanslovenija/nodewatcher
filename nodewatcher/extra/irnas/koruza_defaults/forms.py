from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import forms as registry_forms, registration

from nodewatcher.modules.administration.types import models as type_models
from nodewatcher.modules.administration.projects import models as project_models
from nodewatcher.modules.monitor.sources.http import models as http_models


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
            state.append_item(type_models.TypeConfig, type='koruza')
        elif not type_config.type:
            state.update_item(type_config, type='koruza')

registration.point('node.config').add_form_defaults(DefaultType())


class DefaultProject(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        # If we are not creating a new node, ignore this.
        if not create:
            return

        # Default to project 'KORUZA' in case it exists.
        try:
            koruza_project = project_models.Project.objects.get(name='KORUZA')
        except project_models.Project.DoesNotExist:
            return

        # Choose a default project.
        project_config = state.lookup_item(project_models.ProjectConfig)
        if not project_config:
            state.append_item(project_models.ProjectConfig, project=koruza_project)
        else:
            try:
                if project_config.project:
                    return
            except project_models.Project.DoesNotExist:
                state.update_item(project_config, project=koruza_project)

registration.point('node.config').add_form_defaults(DefaultProject())


class DefaultTelemetrySource(registry_forms.FormDefaults):
    def set_defaults(self, state, create):
        telemetry_config = state.lookup_item(http_models.HttpTelemetrySourceConfig)
        if not telemetry_config:
            state.append_item(http_models.HttpTelemetrySourceConfig, source='push')
        else:
            state.update_item(telemetry_config, source='push')

registration.point('node.config').add_form_defaults(DefaultTelemetrySource())

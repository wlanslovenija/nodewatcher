from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import fields as registry_fields, registration

class ProjectConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes the project a node belongs to.
    """

    project = registry_fields.ModelSelectorKeyField('nodes.Project')

    class RegistryMeta:
        form_order = 2
        registry_id = 'core.project'
        registry_section = _("Project")
        registry_name = _("Basic Project")

registration.point('node.config').register_item(ProjectConfig)

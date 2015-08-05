from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core import models as core_models
from nodewatcher.modules.frontend.statistics import resources


class NodesByProjectResource(resources.StatisticsResource):
    name = 'nodes_by_project'
    description = _("Node distribution among different projects.")

    def get_statistics(self):
        return core_models.Node.objects.regpoint('config').registry_fields(
            project='core.project#project.name'
        ).values(
            'project'
        ).annotate(
            count=models.Count('uuid')
        )

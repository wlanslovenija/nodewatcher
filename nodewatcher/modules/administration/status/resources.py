from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core import models as core_models
from nodewatcher.core.registry import registration
from nodewatcher.modules.frontend.statistics import resources


class NodesByStatusResource(resources.StatisticsResource):
    name = 'nodes_by_status'
    description = _("Distribution of node statuses.")

    def get_header(self):
        return {
            'status': {
                'type': 'string',
                'choices': registration.point('node.monitoring').get_registered_choices('core.status#network').get_json(),
            }
        }

    def get_statistics(self):
        return core_models.Node.objects.regpoint('monitoring').registry_fields(
            status='core.status__network'
        ).values(
            'status'
        ).annotate(
            count=models.Count('uuid')
        )

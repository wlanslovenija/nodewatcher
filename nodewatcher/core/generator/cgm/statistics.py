from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core import models as core_models
from nodewatcher.core.registry import registration
from nodewatcher.modules.frontend.statistics import resources
from nodewatcher.utils import loader


class NodesByDeviceResource(resources.StatisticsResource):
    name = 'nodes_by_device'
    description = _("Device distribution among nodes.")

    def get_header(self):
        # Ensure all CGMs are loaded so that we get all the device metadata.
        loader.load_modules('cgm')

        return {
            'device': {
                'type': 'string',
                'choices': registration.point('node.config').get_registered_choices('core.general#router').get_json(),
            }
        }

    def get_statistics(self):
        return core_models.Node.objects.regpoint('config').registry_fields(
            device='core.general#router'
        ).values(
            'device'
        ).annotate(
            count=models.Count('uuid')
        )

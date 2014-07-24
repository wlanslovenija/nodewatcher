from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import api

# TODO: Temporary, create a way to register fields into an API
from ...administration.status import models as status_models
from ...administration.location import models as location_models


class NodeResource(api.BaseResource):
    class Meta:
        # TODO: Temporary, create a way to register fields into an API
        queryset = core_models.Node.objects.regpoint('config').registry_fields(
            name='core.general#name',
            type='core.type#type',
            router_id='core.routerid#router_id',
            project='core.project#project.name',
            location=location_models.LocationConfig,
        ).regpoint('monitoring').registry_fields(
            last_seen='core.general#last_seen',
            status=status_models.StatusMonitor,
            peers='network.routing.topology#link_count',
            # TODO: Add current clients count?
        # TODO: We should order in the order core.type#type are registered
        ).order_by('type')
        resource_name = 'node'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        max_limit = 5000

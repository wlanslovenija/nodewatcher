from django.contrib.auth import models as auth_models

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import api
from nodewatcher.utils import permissions

from tastypie import resources

# TODO: Temporary, create a way to register fields into an API
from ...administration.status import models as status_models
from ...administration.location import models as location_models


class NodeResource(api.BaseResource):
    class Meta:
        # TODO: Temporary, create a way to register fields into an API
        queryset = core_models.Node.objects.regpoint('config').registry_fields(
            name='core.general#name',
            type='core.type#type',
            router_id='core.routerid',
            project='core.project#project.name',
            location=location_models.LocationConfig.geo_objects.geojson(
                # Request GeoJSON versions of the location.
                field_name='geolocation',
                model_att='geolocation_geojson',
            ),
        ).regpoint('monitoring').registry_fields(
            last_seen='core.general#last_seen',
            status=status_models.StatusMonitor,
            routing_topology='network.routing.topology',
            # TODO: Add current clients count?
        # noqa (PEP8 ignore indentation)
        # We have to have some ordering so that pagination works correctly.
        # Otherwise SKIP and LIMIT does not necessary return expected pages.
        # Later calls to order_by override this so if user specifies an order
        # things work as expected as well.
        ).order_by('uuid')
        resource_name = 'node'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        max_limit = 5000
        ordering = (
            'name',
            'type',
            'project',
            'location',
            'last_seen',
            'status',
            'routing_topology',
            'router_id',
        )
        filtering = {
            'uuid': resources.ALL,
            'name': resources.ALL,
            'type': resources.ALL,
            'project': resources.ALL,
            'location': resources.ALL_WITH_RELATIONS,
            'last_seen': resources.ALL,
            'status': resources.ALL_WITH_RELATIONS,
            'routing_topology': resources.ALL_WITH_RELATIONS,
            'router_id': resources.ALL_WITH_RELATIONS,
        }
        global_filter = (
            'uuid',
            'name',
            'type',
            'project',
        )

    def _after_apply_sorting(self, obj_list, options, order_by_args):
        # We want to augment sorting so that it is always sorted at the end by "uuid" to have a defined order
        # even for keys which are equal between multiple objects. This is necessary for pagination to work correctly,
        # because SKIP and LIMIT works well for pagination only when all objects have a defined order.
        extended_order = list(order_by_args) + ['uuid']
        return obj_list.order_by(*extended_order)

    def _before_apply_filters(self, request, queryset):
        # Used by MyNodesComponent. We use _before_apply_filters so that queryset is modified before count
        # for _nonfiltered_count is taken, so that maintainer filter is not exposed through dataTables.
        maintainer = getattr(request, 'GET', {}).get('maintainer', None)
        if maintainer:
            try:
                maintainer_user = auth_models.User.objects.get(username=maintainer)
                queryset = permissions.get_objects_for_user(maintainer_user, [], queryset, use_superusers=False)
            except auth_models.User.DoesNotExist:
                queryset = queryset.none()

        return queryset

    def get_object_list(self, request):
        queryset = super(NodeResource, self).get_object_list(self)

        # If user specifies a distance parameter, we populate a field with distance from the given
        # geometry to the node. This can then be used to order or filter nodes.
        distance = getattr(request, 'GET', {}).get('distance', None)
        if distance:
            # TODO: GeoQuerySet queries should transform registry field names automatically, so that we do not have to call registry_expand_proxy_field
            queryset = queryset.distance(distance, field_name=queryset.registry_expand_proxy_field('location__geolocation'), model_att='distance')

        return queryset

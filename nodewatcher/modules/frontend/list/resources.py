from django.contrib.auth import models as auth_models

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import api
from nodewatcher.utils import permissions

# TODO: Temporary, create a way to register fields into an API
from ...administration.status import models as status_models
from ...administration.location import models as location_models


class NodeResource(api.BaseResource):
    class Meta:
        # TODO: Temporary, create a way to register fields into an API
        queryset = core_models.Node.objects.regpoint('config').registry_fields(
            name='core.general#name',
            type='core.type#type',
            # TODO: Should we add router id to the snippet as well?
            router_id='core.routerid#router_id',
            project='core.project#project.name',
            location=location_models.LocationConfig,
        ).regpoint('monitoring').registry_fields(
            last_seen='core.general#last_seen',
            status=status_models.StatusMonitor,
            # TODO: Should we add peers and clients to the snippet as well?
            peers='network.routing.topology#link_count',
            # TODO: Add current clients count?
        # TODO: We should order in the order core.type#type are registered
        ).order_by('type')
        resource_name = 'node'
        list_allowed_methods = ('get',)
        detail_allowed_methods = ('get',)
        max_limit = 5000
        # TODO: Sorting by status does not work, how can we map it to order_by string from registry?
        ordering = ('type', 'name', 'last_seen', 'status', 'project')
        # TODO: How can we generate order_by string from registry, without hardcoding registry relations?
        global_filter = ('config_types_typeconfig__type', 'config_core_generalconfig__name', 'monitoring_monitor_generalmonitor__last_seen', 'config_projects_projectconfig__project__name')

    def _before_apply_filters(self, request, queryset):
        # Used by MyNodesComponent. We use _before_apply_filters so that queryset is modified before count
        # for _nonfiltered_count is taken, so that maintainer filter is not exposed through dataTables.
        maintainer = request.GET.get('maintainer', None)
        if maintainer:
            try:
                maintainer_user = auth_models.User.objects.get(username=maintainer)
                queryset = permissions.get_objects_for_user(maintainer_user, [], queryset, use_superusers=False)
            except auth_models.User.DoesNotExist:
                queryset = queryset.none()

        return queryset

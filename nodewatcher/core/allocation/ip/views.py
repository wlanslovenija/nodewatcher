from django.db.models import query

from rest_framework import viewsets, decorators

from nodewatcher.core.api import urls as api_urls
from nodewatcher.core.registry import registration

from . import models, serializers


class IpPoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.IpPool.objects.all()
    serializer_class = serializers.IpPoolSerializer

    def get_queryset(self):
        queryset = super(IpPoolViewSet, self).get_queryset()

        # Support allocated_to queries (list of IP pool allocations for a given object).
        allocated_to = self.request.query_params.get('allocated_to', None)
        if allocated_to:
            allocated_to = allocated_to.split(':')

            if len(allocated_to) == 2:
                base_model, root_id = allocated_to

                # Determine the possible allocation sources.
                allocation_sources = [
                    item
                    for registration_point in registration.all_points() if registration_point.model._meta.model_name == base_model
                    for item in registration_point.config_items() if issubclass(item, models.IpAddressAllocator)
                ]

                # Construct a filter expression.
                q_filter = None
                for src in allocation_sources:
                    field = models.IP_ALLOCATOR_REVERSE_RELATION % {
                        'app_label': src._meta.app_label,
                        'class': src._meta.model_name
                    }
                    q = query.Q(**{'%s__root__pk' % field: root_id})
                    if q_filter is None:
                        q_filter = q
                    else:
                        q_filter |= q

                if q_filter:
                    queryset = queryset.filter(q_filter)

        return queryset

api_urls.v2_api.register('pool/ip', IpPoolViewSet)

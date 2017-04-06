from rest_framework import viewsets

from nodewatcher.core.registry import api as registry_api

from . import models, serializers


class TopologyLinkViewSet(registry_api.RegistryRootViewSetMixin,
                          viewsets.ReadOnlyModelViewSet):
    queryset = models.TopologyLink.objects.all()
    serializer_class = serializers.TopologyLinkSerializer
    registry_root_fields = ['peer']

    def get_queryset(self):
        """
        Augments the queryset to allow filtering.
        """

        queryset = super(TopologyLinkViewSet, self).get_queryset()

        # Filter by node.
        node = self.request.query_params.get('node', None)
        if node is not None:
            queryset = queryset.filter(monitor__root__pk=node)

        # Filter by protocol.
        protocol = self.request.query_params.get('protocol', None)
        if protocol is not None:
            queryset = queryset.filter(monitor__protocol=protocol)

        return queryset

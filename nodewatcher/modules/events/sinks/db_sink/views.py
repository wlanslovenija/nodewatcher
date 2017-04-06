from django.db import models as django_models
from django.views import generic

from rest_framework import filters, viewsets

from nodewatcher.core.registry import api as registry_api

from . import models, permissions, serializers


class EventsList(generic.TemplateView):
    template_name = 'events/list.html'


class EventViewSet(registry_api.RegistryRootViewSetMixin,
                   viewsets.ReadOnlyModelViewSet):
    """
    Endpoint for events.
    """

    queryset = models.SerializedNodeEvent.objects.all()
    serializer_class = serializers.NodeEventSerializer
    permission_classes = (permissions.EventPermission,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ['severity', 'source_name', 'source_type', 'timestamp']
    registry_root_fields = ['related_nodes']

    def get_queryset(self):
        """
        Filter build results for the currently authenticated user.
        """

        qs = super(EventViewSet, self).get_queryset()
        user = self.request.user
        if user.is_authenticated():
            qs = qs.filter(
                django_models.Q(related_users=None) |
                django_models.Q(related_users=user)
            )
        else:
            qs = qs.filter(related_users=None)

        return qs


class WarningViewSet(registry_api.RegistryRootViewSetMixin,
                     viewsets.ReadOnlyModelViewSet):
    """
    Endpoint for warnings.
    """

    queryset = models.SerializedNodeWarning.objects.all()
    serializer_class = serializers.NodeWarningSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ['severity', 'source_name', 'source_type', 'first_seen', 'last_seen']
    registry_root_fields = ['related_nodes']

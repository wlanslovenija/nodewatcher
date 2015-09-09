from django import shortcuts
from django.conf import urls

from tastypie import utils

from . import models as core_models


# TODO: This is a temporary hack until we have proper https://dev.wlan-si.net/ticket/1268.
class NodeSubresourceMixin(object):
    def prepend_urls(self):
        return [
            urls.url(r'^node/(?P<node_id>[\w\d_.-]+)/(?P<resource_name>%s)%s$' % (self._meta.resource_name, utils.trailing_slash()), self.wrap_view('dispatch_node'), name='api_dispatch_node'),
        ]

    def dispatch_node(self, request, **kwargs):
        node = shortcuts.get_object_or_404(core_models.Node, pk=kwargs.pop('node_id'))
        request._filter_node = node
        return self.dispatch_list(request, **kwargs)

    def get_object_list(self, request):
        objects = super(NodeSubresourceMixin, self).get_object_list(request)

        if hasattr(request, '_filter_node'):
            objects = objects.filter(**{self._meta.node_filter: request._filter_node})

        return objects

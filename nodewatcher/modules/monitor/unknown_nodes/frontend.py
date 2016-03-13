from django.conf import urls
from django.core import urlresolvers

from nodewatcher.core.api import urls as api_urls
from nodewatcher.core.frontend import components

from . import resources, views


class UnknownNodesComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(UnknownNodesComponent, cls).get_urls() + [
            urls.url(r'^my/unknown_nodes/$', views.ListUnknownNodes.as_view(), name='list'),
            urls.url(r'^my/unknown_nodes/register/(?P<uuid>[^/]+)/$', views.RegisterUnknownNode.as_view(), name='register'),
        ]

components.pool.register(UnknownNodesComponent)


api_urls.v1_api.register(resources.UnknownNodeResource())


components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("My Unknown Nodes"),
    url=urlresolvers.reverse_lazy('UnknownNodesComponent:list'),
    weight=80,
    visible=lambda menu_entry, request, context: request.user.is_superuser,
))

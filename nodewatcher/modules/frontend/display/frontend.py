from django.conf import urls
from django.utils.translation import ugettext_lazy as _

from guardian import shortcuts

from nodewatcher.core.frontend import components

from . import views


class DisplayComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(DisplayComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'^node/(?P<pk>[^/]+)/$', views.DisplayNode.as_view(), name='node'),
        )

components.pool.register(DisplayComponent)


components.menus.register(components.Menu('node_menu'))


components.partials.register(components.Partial('node_general_partial'))

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='name',
    template='nodes/general/name.html',
    weight=-1,
    extra_context=lambda context: {} if 'node_name' in context else {
        'node_name': getattr(context['node'].config.core.general(), 'name', None) or _("unknown")
    },
))

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='router_id',
    template='nodes/general/router_id.html',
    weight=100,
    extra_context=lambda context: {
        'router_ids': context['node'].config.core.routerid()
    },
))


components.partials.register(components.Partial('node_display_partial'))

components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='general',
    template='nodes/general_partial.html',
))

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='maintainers',
    template='nodes/general/maintainers.html',
    extra_context=lambda context: {
        'maintainers': shortcuts.get_users_with_perms(context['node']),
    },
))

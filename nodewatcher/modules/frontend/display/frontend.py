from django.conf import urls
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.frontend import components
from nodewatcher.core.registry import exceptions

from . import views


class DisplayComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(DisplayComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'^node/(?P<pk>[^/]+)/$', views.DisplayNode.as_view(), name='node'),
        )

components.pool.register(DisplayComponent)

components.menus.register(components.Menu('display_node_menu'))

components.partials.register(components.Partial('node_snippet_partial'))

components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='name',
    template='nodes/snippet/name.html',
    weight=-1,
    extra_context=lambda context: {} if 'node_name' in context else {
        'node_name': getattr(context['node'].config.core.general(), 'name', None) or _("unknown")
    },
))


def node_last_seen(context):
    try:
        last_seen = context['node'].monitoring.core.general().last_seen
    except (exceptions.RegistryItemNotRegistered, AttributeError):
        last_seen = None

    return {
        'node_last_seen': last_seen or _("unknown")
    }

components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='last_seen',
    template='nodes/snippet/last_seen.html',
    extra_context=node_last_seen,
))

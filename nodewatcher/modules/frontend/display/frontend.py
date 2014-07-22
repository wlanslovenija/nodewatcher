from django.conf import urls
from django.utils.translation import ugettext_lazy as _

from guardian import shortcuts

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
    except exceptions.RegistryItemNotRegistered:
        # If module is not loaded we want it to be false
        last_seen = None
    except AttributeError:
        # If attribute does not exist (module is loaded by no monitoring data is available), we display "unknown"
        last_seen = _("unknown")

    return {
        'node_last_seen': last_seen
    }

components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='last_seen',
    template='nodes/snippet/last_seen.html',
    extra_context=node_last_seen,
))


components.partials.register(components.Partial('node_display_partial'))

components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='snippet',
    template='nodes/display/snippet.html',
))

components.partials.get_partial('node_display_partial').add(components.PartialEntry(
    name='maintainers',
    template='nodes/display/maintainers.html',
    extra_context=lambda context: {
        'maintainers': shortcuts.get_users_with_perms(context['node']),
    },
))

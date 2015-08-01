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


components.partials.register(components.Partial('node_snippet_partial'))

components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='name',
    template='nodes/snippet/name.html',
    weight=-1,
    extra_context=lambda context: {} if 'node_name' in context else {
        'node_name': getattr(context['node'].config.core.general(), 'name', None) or _("unknown")
    },
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

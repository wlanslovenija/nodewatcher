from django.conf import urls
from django.utils.translation import ugettext_lazy as _

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

components.menus.register(components.Menu('display_node_menu'))

components.partials.register(components.Partial('node_snippet_partial'))

components.partials.get_partial('node_snippet_partial').add(components.PartialEntry(
    name='name',
    template='nodes/snippet/name.html',
    extra_context=lambda context: {} if 'node_name' in context else {
        'node_name': context['node'].config.core.general().name or _("unknown")
    },
))

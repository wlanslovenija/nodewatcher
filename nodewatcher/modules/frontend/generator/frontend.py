from django.conf import urls
from django.core import urlresolvers

from nodewatcher.core.frontend import components

from . import views


class GeneratorComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(GeneratorComponent, cls).get_urls() + urls.patterns(
            '',

            urls.url(r'^node/(?P<pk>[^/]+)/generate_firmware/$', views.GenerateFirmware.as_view(), name='generate_firmware'),

            urls.url(r'^generator/build/(?P<pk>[^/]+)$', views.ViewBuild.as_view(), name='view_build'),
        )

components.pool.register(GeneratorComponent)


components.menus.get_menu('display_node_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Generate Firmware"),
    url=lambda menu_entry, context: urlresolvers.reverse('GeneratorComponent:generate_firmware', kwargs={'pk': context['node'].pk}),
    visible=lambda menu_entry, request, context: request.user.has_perm('generate_firmware', context['node']),
))

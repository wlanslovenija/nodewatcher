from django.conf import urls
from django.core import urlresolvers

from nodewatcher.core.frontend import api, components

from . import resources, views


class GeneratorComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(GeneratorComponent, cls).get_urls() + [
            urls.url(r'^node/(?P<pk>[^/]+)/generate_firmware/$', views.GenerateFirmware.as_view(), name='generate_firmware'),

            urls.url(r'^my/builds/$', views.ListBuilds.as_view(), name='list_builds'),
            urls.url(r'^my/builds/(?P<pk>[^/]+)/$', views.ViewBuild.as_view(), name='view_build'),
        ]

components.pool.register(GeneratorComponent)


api.v1_api.register(resources.BuildResultResource())
api.v1_api.register(resources.BuildResultFileResource())
api.v1_api.register(resources.BuilderResource())
api.v1_api.register(resources.BuildChannelResource())
api.v1_api.register(resources.BuildVersionResource())


components.menus.get_menu('node_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Generate Firmware"),
    url=lambda menu_entry, context: urlresolvers.reverse('GeneratorComponent:generate_firmware', kwargs={'pk': context['node'].pk}),
    visible=lambda menu_entry, request, context: request.user.has_perm('core.generate_firmware', context['node']),
))

components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("My Firmware Builds"),
    url=urlresolvers.reverse_lazy('GeneratorComponent:list_builds'),
    visible=lambda menu_entry, request, context: request.user.is_authenticated(),
))

components.partials.register(components.Partial('generator_view_build_partial'))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='node',
    template='nodes/general/name.html',
    extra_context=lambda context: {} if 'node' in context else {
        'node': context['build'].node
    },
))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='created',
    template='generator/build/created.html',
))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='updated',
    template='generator/build/updated.html',
))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='status',
    template='generator/build/status.html',
))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='channel',
    template='generator/build/channel.html',
))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='channel',
    template='generator/builder/name.html',
    extra_context=lambda context: {} if 'builder' in context else {
        'builder': context['build'].builder
    },
))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='channel',
    template='generator/builder/version.html',
    extra_context=lambda context: {} if 'builder' in context else {
        'builder': context['build'].builder
    },
))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='files',
    template='generator/build/files.html',
))

components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='log',
    template='generator/build/log.html',
))

from django.conf import urls
from django.core import urlresolvers

from nodewatcher.core import api
from nodewatcher.core.frontend import components

from . import resources, views


class PublicKeyComponent(components.FrontendComponent):
    @classmethod
    def get_urls(cls):
        return super(PublicKeyComponent, cls).get_urls() + [
            urls.url(r'^my/public_keys/$', views.ListPublicKeys.as_view(), name='list'),
            urls.url(r'^my/public_keys/add/$', views.AddPublicKey.as_view(), name='add'),
            urls.url(r'^my/public_keys/(?P<pk>[^/]+)/remove/$', views.RemovePublicKey.as_view(), name='remove'),
        ]

components.pool.register(PublicKeyComponent)


api.v1_api.register(resources.UserAuthenticationKeyResource())


components.menus.register(components.Menu('public_key_menu'))


components.menus.get_menu('accounts_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("My Public Keys"),
    url=urlresolvers.reverse_lazy('PublicKeyComponent:list'),
    visible=lambda menu_entry, request, context: request.user.is_authenticated(),
))

components.menus.get_menu('public_key_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("Add Public Key"),
    url=lambda menu_entry, context: urlresolvers.reverse('PublicKeyComponent:add'),
))

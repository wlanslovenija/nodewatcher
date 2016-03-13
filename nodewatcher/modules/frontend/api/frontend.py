from django.core import urlresolvers

from nodewatcher.core.frontend import components


components.menus.get_menu('main_menu').add(components.MenuEntry(
    label=components.ugettext_lazy("API"),
    url=urlresolvers.reverse_lazy('apiv2:api-root'),
))

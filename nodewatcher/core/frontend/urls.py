from django.conf import urls

from . import components, api

# We are using context manager here because this is a special case
# "menus.register" is not near the end of the module as usual and
# "components.pool.discover_components" imports many modules so
# chances of an exception are high, so we take extra care here
with components.menus:
    # Has to be before auto-discovery
    components.menus.register(components.Menu('main_menu'))
    components.menus.register(components.Menu('accounts_menu'))

    # Frontend components auto-discovery
    components.pool.discover_components()

    urlpatterns = components.pool.get_urls() + [
        urls.url(r'^api/v2/', urls.include(api.router.urls)),
    ]

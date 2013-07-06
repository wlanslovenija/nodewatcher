from . import components

# Has to be before auto-discovery
components.menus.register(components.Menu('main_menu'))

# Frontend components auto-discovery
components.pool.discover_components()

urlpatterns = components.pool.get_urls()

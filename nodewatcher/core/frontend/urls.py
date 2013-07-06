from . import components

# Frontend components auto-discovery
components.pool.discover_components()

urlpatterns = components.pool.get_urls()

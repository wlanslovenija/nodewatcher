from django.apps import apps
from django.contrib import admin

from polymorphic import admin as polymorphic_admin

from . import models


class TunneldiggerServerChildAdmin(polymorphic_admin.PolymorphicChildModelAdmin):
    base_model = models.TunneldiggerServer


class TunneldiggerServerAdmin(polymorphic_admin.PolymorphicParentModelAdmin):
    base_model = models.TunneldiggerServer
    child_models = [
        (models.TunneldiggerServer, TunneldiggerServerChildAdmin),
    ]
    list_display = ('name', 'address', 'ports', 'enabled')

# In case projects module is installed, we support per-project server configuration.
if apps.is_installed('nodewatcher.modules.administration.projects'):
    class PerProjectTunneldiggerServerAdmin(TunneldiggerServerChildAdmin):
        pass

    TunneldiggerServerAdmin.child_models.append(
        (models.PerProjectTunneldiggerServer, PerProjectTunneldiggerServerAdmin)
    )

admin.site.register(models.TunneldiggerServer, TunneldiggerServerAdmin)

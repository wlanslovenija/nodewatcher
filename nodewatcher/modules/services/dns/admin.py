from django.apps import apps
from django.contrib import admin

from polymorphic import admin as polymorphic_admin

from . import models


class DnsServerChildAdmin(polymorphic_admin.PolymorphicChildModelAdmin):
    base_model = models.DnsServer


class DnsServerAdmin(polymorphic_admin.PolymorphicParentModelAdmin):
    base_model = models.DnsServer
    child_models = [
        (models.DnsServer, DnsServerChildAdmin),
    ]
    list_display = ('name', 'address', 'enabled')

# In case projects module is installed, we support per-project server configuration.
if apps.is_installed('nodewatcher.modules.administration.projects'):
    class PerProjectDnsServerAdmin(DnsServerChildAdmin):
        pass

    DnsServerAdmin.child_models.append(
        (models.PerProjectDnsServer, PerProjectDnsServerAdmin)
    )

admin.site.register(models.DnsServer, DnsServerAdmin)

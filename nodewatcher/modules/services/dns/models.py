from django.apps import apps
from django.db import models
from django.utils.translation import ugettext_lazy as _

import polymorphic

from nodewatcher.core.registry import fields as registry_fields, registration


class DnsServer(polymorphic.PolymorphicModel):
    """
    DNS server configuration.
    """

    name = models.CharField(max_length=100)
    address = registry_fields.IPAddressField(host_required=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("DNS server")

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.address)

# In case projects module is installed, we support per-project server configuration.
if apps.is_installed('nodewatcher.modules.administration.projects'):
    from nodewatcher.modules.administration.projects import models as projects_models

    class PerProjectDnsServer(DnsServer):
        project = models.ForeignKey(projects_models.Project, related_name='+')

        class Meta:
            verbose_name = _("Project-specific DNS server")


class DnsServerConfig(registration.bases.NodeConfigRegistryItem):
    """
    Per-node DNS server address configuration.
    """

    server = registry_fields.ModelRegistryChoiceField(DnsServer, limit_choices_to={'enabled': True})

    class RegistryMeta:
        form_weight = 60
        registry_id = 'core.servers.dns'
        registry_section = _("DNS Servers")
        registry_name = _("DNS Server")
        multiple = True

registration.point('node.config').register_item(DnsServerConfig)

from django.apps import apps
from django.db import models
from django.utils.translation import ugettext_lazy as _

import polymorphic

# TODO: This import will not be needed once we upgrade to Django 1.8.
from postgres import fields as postgres_fields

from nodewatcher.core import validators as core_validators
from nodewatcher.core.registry import fields as registry_fields, registration
from nodewatcher.core.generator.cgm import models as cgm_models


class TunneldiggerServer(polymorphic.PolymorphicModel):
    """
    Tunneldigger server configuration.
    """

    name = models.CharField(max_length=100)
    address = registry_fields.IPAddressField(host_required=True)
    ports = postgres_fields.ArrayField(
        models.IntegerField(validators=[core_validators.PortNumberValidator()])
    )
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Tunneldigger server")

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.address)

# In case projects module is installed, we support per-project server configuration.
if apps.is_installed('nodewatcher.modules.administration.projects'):
    from nodewatcher.modules.administration.projects import models as projects_models

    class PerProjectTunneldiggerServer(TunneldiggerServer):
        project = models.ForeignKey(projects_models.Project, related_name='+')

        class Meta:
            verbose_name = _("Project-specific tunneldigger server")


class TunneldiggerInterfaceConfig(cgm_models.InterfaceConfig, cgm_models.RoutableInterface):
    """
    Tunneldigger VPN interface.
    """

    mac = registry_fields.MACAddressField(auto_add=True)
    server = registry_fields.ModelRegistryChoiceField(TunneldiggerServer, limit_choices_to={'enabled': True})
    uplink_interface = registry_fields.ReferenceChoiceField(
        cgm_models.InterfaceConfig,
        # Limit choices to interfaces selected as uplinks.
        limit_choices_to=lambda model: getattr(model, 'uplink', False),
        related_name='+',
        help_text=_("Select this if you want to bind the tunnel only to a specific interface."),
    )

    class RegistryMeta(cgm_models.InterfaceConfig.RegistryMeta):
        registry_name = _("Tunneldigger Interface")

registration.point('node.config').register_item(TunneldiggerInterfaceConfig)
registration.point('node.config').register_subitem(TunneldiggerInterfaceConfig, cgm_models.ThroughputInterfaceLimitConfig)


def get_tunneldigger_interface_name(index):
    """
    Returns the interface name of a tunneldigger interface with a specific
    index.

    :param index: Interface index
    """

    return "digger%d" % index

from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core import validators as core_validators
from nodewatcher.core.registry import fields as registry_fields, registration
from nodewatcher.core.generator.cgm import models as cgm_models


class TunneldiggerInterfaceConfig(cgm_models.InterfaceConfig, cgm_models.RoutableInterface):
    """
    Tunneldigger VPN interface.
    """

    mac = registry_fields.MACAddressField(auto_add=True)

    class RegistryMeta(cgm_models.InterfaceConfig.RegistryMeta):
        registry_name = _("Tunneldigger Interface")

registration.point('node.config').register_item(TunneldiggerInterfaceConfig)
registration.point('node.config').register_subitem(TunneldiggerInterfaceConfig, cgm_models.ThroughputInterfaceLimitConfig)


class TunneldiggerServerConfig(registration.bases.NodeConfigRegistryItem):
    """
    Tunneldigger server configuration.
    """

    tunnel = registry_fields.IntraRegistryForeignKey(
        TunneldiggerInterfaceConfig,
        editable=False,
        null=False,
        related_name='servers'
    )
    address = registry_fields.IPAddressField(host_required=True)
    port = models.IntegerField(validators=[core_validators.PortNumberValidator()])

    class RegistryMeta:
        form_weight = 51
        registry_id = 'core.servers.tunneldigger'
        registry_section = _("Tunneldigger Servers")
        registry_name = _("Tunneldigger Server")
        multiple = True

registration.point('node.config').register_subitem(TunneldiggerInterfaceConfig, TunneldiggerServerConfig)


def get_tunneldigger_interface_name(index):
    """
    Returns the interface name of a tunneldigger interface with a specific
    index.

    :param index: Interface index
    """

    return "digger%d" % index

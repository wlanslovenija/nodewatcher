from django.db import models
from django.utils.translation import ugettext as _

from .registry import fields as registry_fields, registration

# Create registration point
registration.create_point('nodes.Node', 'config')

class GeneralConfig(registration.bases.NodeConfigRegistryItem):
    """
    General node configuration containing basic parameters about the
    node.
    """

    name = models.CharField(max_length = 30)

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 1
        registry_id = 'core.general'
        registry_section = _("General Configuration")
        registry_name = _("Basic Configuration")
        lookup_proxies = ['name']

# TODO: Validate node name via regexp: NODE_NAME_RE = re.compile(r'^[a-z](?:-?[a-z0-9]+)*$')

registration.point('node.config').register_item(GeneralConfig)

class RouterIdConfig(registration.bases.NodeConfigRegistryItem):
    """
    Router identifier configuration.
    """

    router_id = models.CharField(max_length = 100)
    family = registry_fields.SelectorKeyField('node.config', 'core.routerid#family')

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 100
        registry_id = 'core.routerid'
        multiple = True
        hidden = True

registration.point('node.config').register_choice('core.routerid#family', 'ipv4', _("IPv4"))
registration.point('node.config').register_choice('core.routerid#family', 'ipv6', _("IPv6"))
registration.point('node.config').register_item(RouterIdConfig)

# TODO: Move together with the rest to modules.administration.addressing
from .allocation.ip import models as ip_models

# TODO: Move to modules.administration.addressing
class BasicAddressingConfig(registration.bases.NodeConfigRegistryItem, ip_models.IpAddressAllocator):
    """
    Enables allocation of subnets for the node without the need to define any interfaces.
    """

    class Meta:
        app_label = "core"

    class RegistryMeta:
        form_order = 51
        registry_id = 'core.basic-addressing'
        registry_section = _("Subnet Allocation")
        registry_name = _("Subnet")
        multiple = True

registration.point('node.config').register_item(BasicAddressingConfig)

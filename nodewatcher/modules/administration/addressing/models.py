from django.utils.translation import ugettext as _

from nodewatcher.core.allocation.ip import models as ip_models
from nodewatcher.core.registry import registration

class BasicAddressingConfig(registration.bases.NodeConfigRegistryItem, ip_models.IpAddressAllocator):
    """
    Enables allocation of subnets for the node without the need to define any interfaces.
    """

    class RegistryMeta:
        form_order = 51
        registry_id = 'core.basic-addressing'
        registry_section = _("Subnet Allocation")
        registry_name = _("Subnet")
        multiple = True

registration.point('node.config').register_item(BasicAddressingConfig)

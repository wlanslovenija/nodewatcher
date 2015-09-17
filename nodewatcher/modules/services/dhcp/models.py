from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import fields as registry_fields, registration


class DhcpLeaseConfig(registration.bases.NodeConfigRegistryItem):
    """
    DHCP lease configuration.
    """

    mac_address = registry_fields.MACAddressField(verbose_name=_("MAC Address"))
    ip_address = registry_fields.IPAddressField(host_required=True, verbose_name=_("IP address"))
    hostname = models.CharField(max_length=50, null=True, blank=True)

    class RegistryMeta:
        form_weight = 55
        registry_id = 'core.dhcp.leases'
        registry_section = _("DHCP Leases")
        registry_name = _("DHCP Lease")
        multiple = True

registration.point('node.config').register_item(DhcpLeaseConfig)

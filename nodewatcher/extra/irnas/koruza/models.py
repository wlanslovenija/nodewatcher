from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import registration, fields as registry_fields


class KoruzaNetworkMeasurementConfig(cgm_models.PackageConfig):
    """
    KORUZA network measurement package configuration.
    """

    role = registry_fields.RegistryChoiceField('node.config', 'irnas.koruza.netmeasure#role', default='primary')

    class RegistryMeta(cgm_models.PackageConfig.RegistryMeta):
        registry_name = _("IRNAS KORUZA Network Measurement")

registration.point('node.config').register_choice('irnas.koruza.netmeasure#role', registration.Choice('primary', _("Primary")))
registration.point('node.config').register_choice('irnas.koruza.netmeasure#role', registration.Choice('secondary', _("Secondary")))
registration.point('node.config').register_item(KoruzaNetworkMeasurementConfig)


class KoruzaVpnMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    KORUZA VPN information.
    """

    ip_address = registry_fields.IPAddressField(null=True)

    class RegistryMeta:
        registry_id = 'koruza.vpn'

registration.point('node.monitoring').register_item(KoruzaVpnMonitor)


class KoruzaLinkMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    KORUZA link information.
    """

    neighbour = models.ForeignKey(core_models.Node, related_name='+', null=True)

    class RegistryMeta:
        registry_id = 'koruza.link'

registration.point('node.monitoring').register_item(KoruzaLinkMonitor)

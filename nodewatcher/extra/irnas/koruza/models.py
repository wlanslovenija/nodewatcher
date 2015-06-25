from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core import models as core_models
from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import registration, fields as registry_fields


class KoruzaConfig(cgm_models.PackageConfig):
    """
    KORUZA controller unit configuration.
    """

    serial_port = registry_fields.RegistryChoiceField('node.config', 'irnas.koruza#serial_port', default='usb0')
    peer_controller = models.ForeignKey(core_models.Node, blank=True, null=True, related_name='+')

    class RegistryMeta(cgm_models.PackageConfig.RegistryMeta):
        registry_name = _("IRNAS KORUZA Controller")

registration.point('node.config').register_choice('irnas.koruza#serial_port', registration.Choice('usb0', _("USB0")))
registration.point('node.config').register_choice('irnas.koruza#serial_port', registration.Choice('usb1', _("USB1")))
registration.point('node.config').register_item(KoruzaConfig)

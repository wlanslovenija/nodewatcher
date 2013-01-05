from django.core import exceptions
from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import fields as registry_fields, registration

class WifiRadioEquipmentConfig(registration.bases.NodeConfigRegistryItem):
    """
    General type of equipment that can be attached to a wireless
    radio device.
    """

    device = registry_fields.IntraRegistryForeignKey(
        cgm_models.WifiRadioDeviceConfig, editable = False, null = False, related_name = 'equipment'
    )

    class RegistryMeta:
        form_order = 50
        registry_id = 'core.equipment.radio'
        registry_section = _("Radio Equipment")
        registry_name = _("Generic Radio Equipment")
        multiple = True
        hidden = True

registration.point('node.config').register_subitem(cgm_models.WifiRadioDeviceConfig, WifiRadioEquipmentConfig)

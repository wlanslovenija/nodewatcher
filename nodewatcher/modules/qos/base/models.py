from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import fields as registry_fields, registration


class InterfaceQoSConfig(registration.bases.NodeConfigRegistryItem):
    """
    Configuration of per-interface QoS.
    """

    interface = registry_fields.IntraRegistryForeignKey(
        cgm_models.InterfaceConfig, editable=False, null=False, related_name='qos'
    )
    upload = models.PositiveIntegerField(
        verbose_name=_("Upload speed"),
        default=0,
        help_text=_("Enter the upload speed in kbit/s, set to zero to disable upload limit.")
    )
    download = models.PositiveIntegerField(
        verbose_name=_("Download speed"),
        default=0,
        help_text=_("Enter the download speed in kbit/s, set to zero to disable download limit.")
    )
    enabled = models.BooleanField(default=True)

    class RegistryMeta:
        form_weight = 50
        registry_id = 'core.interfaces.qos'
        registry_section = _("QoS Configuration")
        registry_name = _("Basic QoS")
        multiple = True

registration.point('node.config').register_subitem(cgm_models.InterfaceConfig, InterfaceQoSConfig)
registration.point('node.config').register_subitem(cgm_models.EthernetInterfaceConfig, InterfaceQoSConfig)
registration.point('node.config').register_subitem(cgm_models.WifiInterfaceConfig, InterfaceQoSConfig)

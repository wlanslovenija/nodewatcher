from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import registration


class DescriptionConfig(registration.bases.NodeConfigRegistryItem):
    """
    Textual description of a node.
    """

    notes = models.TextField(
        blank=True,
        default='',
        help_text=_("The notes field is private and is shown only to node maintainers."),
    )
    url = models.URLField(blank=True, default='', verbose_name=_("URL"))

    class RegistryMeta:
        form_weight = 4
        registry_id = 'core.description'
        registry_section = _("Description")
        registry_name = _("Basic Description")

registration.point('node.config').register_item(DescriptionConfig)

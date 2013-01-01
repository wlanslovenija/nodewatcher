from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import fields as registry_fields, registration

class TypeConfig(registration.bases.NodeConfigRegistryItem):
    """
    Type configuration determines the type of the node.
    """

    type = registry_fields.SelectorKeyField('node.config', 'core.type#type')

    class RegistryMeta:
        form_order = 2
        registry_id = 'core.type'
        registry_section = _("Type Configuration")
        registry_name = _("Type Configuration")
        lookup_proxies = ['type']

# Register possible node types
registration.point('node.config').register_choice('core.type#type', 'wireless', _("Wireless"))
registration.point('node.config').register_choice('core.type#type', 'server', _("Server"))
registration.point('node.config').register_choice('core.type#type', 'mobile', _("Mobile"))
registration.point('node.config').register_choice('core.type#type', 'test', _("Test"))
registration.point('node.config').register_choice('core.type#type', 'dead', _("Dead"))
registration.point('node.config').register_choice('core.type#type', 'unknown', _("Unknown"))
registration.point('node.config').register_item(TypeConfig)

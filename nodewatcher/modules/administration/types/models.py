from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import fields as registry_fields, registration


class TypeConfig(registration.bases.NodeConfigRegistryItem):
    """
    Type configuration determines the type of the node.
    """

    type = registry_fields.RegistryChoiceField('node.config', 'core.type#type', null=True)

    class RegistryMeta:
        form_weight = 2
        registry_id = 'core.type'
        registry_section = _("Type Configuration")
        registry_name = _("Type Configuration")
        lookup_proxies = ['type']

# Register possible node types
registration.point('node.config').register_choice('core.type#type', registration.Choice('server', _("Server"), icon="node-type-server"))
registration.point('node.config').register_choice('core.type#type', registration.Choice('wireless', _("Wireless"), icon="node-type-wireless"))
registration.point('node.config').register_choice('core.type#type', registration.Choice('test', _("Test"), icon="node-type-test"))
registration.point('node.config').register_choice('core.type#type', registration.Choice('mobile', _("Mobile"), icon="node-type-mobile"))
registration.point('node.config').register_choice('core.type#type', registration.Choice('dead', _("Dead"), icon="node-type-dead"))
registration.point('node.config').register_choice('core.type#type', registration.Choice(None, _("Unknown"), icon="node-unknown"))
registration.point('node.config').register_item(TypeConfig)

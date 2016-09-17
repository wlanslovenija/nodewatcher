from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import fields as registry_fields, registration


class RoleConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes a single node's roles.
    """

    roles = registry_fields.RegistryMultipleChoiceField(
        'node.config', 'core.roles#roles',
        blank=True, null=True, default=list,
    )

    class RegistryMeta:
        form_weight = 20
        registry_id = 'core.roles'
        registry_section = _("Node Roles")
        registry_name = _("Node Roles")

registration.point("node.config").register_choice(
    'core.roles#roles',
    registration.Choice(
        'system', _("System node"),
        help_text=_("The node has an important system function, required for network operation."),
    )
)
registration.point("node.config").register_choice(
    'core.roles#roles',
    registration.Choice(
        'border-router', _("Border router"),
        help_text=_("The node is a border router, enabling access to external networks."),
    )
)
registration.point("node.config").register_choice(
    'core.roles#roles',
    registration.Choice(
        'vpn-server', _("VPN server"),
        help_text=_("The node provides a VPN server for other nodes."),
    )
)
registration.point("node.config").register_choice(
    'core.roles#roles',
    registration.Choice(
        'redundancy-required', _("Node with redundant links requirement"),
        help_text=_("The node requires multiple redundant links."),
    )
)
registration.point("node.config").register_item(RoleConfig)

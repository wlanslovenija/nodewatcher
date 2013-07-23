from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import registration


class RoleConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes a single node's role.
    """

    class RegistryMeta:
        form_order = 20
        registry_id = 'core.roles'
        registry_section = _("Node Roles")
        registry_name = _("Generic Role")
        multiple = True
        multiple_static = True
        hidden = True

registration.point("node.config").register_item(RoleConfig)


class SystemRoleConfig(RoleConfig):
    """
    Describes the "system" role.
    """

    system = models.BooleanField(default=False)

    class RegistryMeta(RoleConfig.RegistryMeta):
        registry_name = _("System Role")

registration.point('node.config').register_item(SystemRoleConfig)


class BorderRouterRoleConfig(RoleConfig):
    """
    Describes the "border router" role.
    """

    border_router = models.BooleanField(default=False)

    class RegistryMeta(RoleConfig.RegistryMeta):
        registry_name = _("Border Router Role")

registration.point('node.config').register_item(BorderRouterRoleConfig)


class VpnServerRoleConfig(RoleConfig):
    """
    Describes the "vpn server" role.
    """

    vpn_server = models.BooleanField(default=False)

    class RegistryMeta(RoleConfig.RegistryMeta):
        registry_name = _("VPN Server Role")

registration.point('node.config').register_item(VpnServerRoleConfig)


class RedundantNodeRoleConfig(RoleConfig):
    """
    Describes the "redundant node" role.
    """

    redundancy_required = models.BooleanField(default=False)

    class RegistryMeta(RoleConfig.RegistryMeta):
        registry_name = _("Redundant Node Role")

registration.point('node.config').register_item(RedundantNodeRoleConfig)

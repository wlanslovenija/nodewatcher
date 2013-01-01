from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import ugettext as _

from .registry import fields as registry_fields, registration

# Create registration point
registration.create_point('nodes.Node', 'config')

class GeneralConfig(registration.bases.NodeConfigRegistryItem):
    """
    General node configuration containing basic parameters about the
    node.
    """

    name = models.CharField(max_length = 30)

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 1
        registry_id = 'core.general'
        registry_section = _("General Configuration")
        registry_name = _("Basic Configuration")
        lookup_proxies = ['name']

# TODO: Validate node name via regexp: NODE_NAME_RE = re.compile(r'^[a-z](?:-?[a-z0-9]+)*$')

registration.point('node.config').register_item(GeneralConfig)

class RouterIdConfig(registration.bases.NodeConfigRegistryItem):
    """
    Router identifier configuration.
    """

    router_id = models.CharField(max_length = 100)
    family = registry_fields.SelectorKeyField('node.config', 'core.routerid#family')

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 100
        registry_id = 'core.routerid'
        multiple = True
        hidden = True

registration.point('node.config').register_choice('core.routerid#family', 'ipv4', _("IPv4"))
registration.point('node.config').register_choice('core.routerid#family', 'ipv6', _("IPv6"))
registration.point('node.config').register_item(RouterIdConfig)

# TODO: This should be moved to modules.administration.projects
class ProjectConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes the project a node belongs to.
    """

    project = registry_fields.ModelSelectorKeyField('nodes.Project')

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 2
        registry_id = 'core.project'
        registry_section = _("Project")
        registry_name = _("Basic Project")

registration.point('node.config').register_item(ProjectConfig)

# TODO: This should be moved to modules.administration.location
class LocationConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes the location of a node.
    """

    address = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100) # TODO city field?
    country = models.CharField(max_length = 100) # TODO country field?
    geolocation = gis_models.PointField(null = True)
    altitude = models.FloatField(default = 0)

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 3
        registry_id = 'core.location'
        registry_section = _("Location")
        registry_name = _("Basic Location")

registration.point('node.config').register_item(LocationConfig)

# TODO: Move to modules.administration.description
class DescriptionConfig(registration.bases.NodeConfigRegistryItem):
    """
    Textual description of a node.
    """

    notes = models.TextField(blank = True, default = '')
    url = models.URLField(verify_exists = False, blank = True, default = '', verbose_name = _("URL"))

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 4
        registry_id = 'core.description'
        registry_section = _("Description")
        registry_name = _("Basic Description")

registration.point('node.config').register_item(DescriptionConfig)

# TODO: Move together with the rest to modules.administration.addressing
from .allocation.ip import models as ip_models

# TODO: Move to modules.administration.addressing
class BasicAddressingConfig(registration.bases.NodeConfigRegistryItem, ip_models.IpAddressAllocator):
    """
    Enables allocation of subnets for the node without the need to define any interfaces.
    """

    class Meta:
        app_label = "core"

    class RegistryMeta:
        form_order = 51
        registry_id = 'core.basic-addressing'
        registry_section = _("Subnet Allocation")
        registry_name = _("Subnet")
        multiple = True

registration.point('node.config').register_item(BasicAddressingConfig)

# TODO: Move to modules.administration.roles
class RoleConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes a single node's role.
    """

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 20
        registry_id = 'core.roles'
        registry_section = _("Node Roles")
        registry_name = _("Generic Role")
        multiple = True
        multiple_static = True
        hidden = True

registration.point("node.config").register_item(RoleConfig)

# TODO: Move to modules.administration.roles
class SystemRoleConfig(RoleConfig):
    """
    Describes the "system" role.
    """

    system = models.BooleanField(default = False)

    class Meta:
        app_label = 'core'

    class RegistryMeta(RoleConfig.RegistryMeta):
        registry_name = _("System Role")

registration.point('node.config').register_item(SystemRoleConfig)

# TODO: Move to modules.administration.roles
class BorderRouterRoleConfig(RoleConfig):
    """
    Describes the "border router" role.
    """

    border_router = models.BooleanField(default = False)

    class Meta:
        app_label = 'core'

    class RegistryMeta(RoleConfig.RegistryMeta):
        registry_name = _("Border Router Role")

registration.point('node.config').register_item(BorderRouterRoleConfig)

# TODO: Move to modules.administration.roles
class VpnServerRoleConfig(RoleConfig):
    """
    Describes the "vpn server" role.
    """

    vpn_server = models.BooleanField(default = False)

    class Meta:
        app_label = 'core'

    class RegistryMeta(RoleConfig.RegistryMeta):
        registry_name = _("VPN Server Role")

registration.point('node.config').register_item(VpnServerRoleConfig)

# TODO: Move to modules.administration.roles
class RedundantNodeRoleConfig(RoleConfig):
    """
    Describes the "redundant node" role.
    """

    redundancy_required = models.BooleanField(default = False)

    class Meta:
        app_label = 'core'

    class RegistryMeta(RoleConfig.RegistryMeta):
        registry_name = _("Redundant Node Role")

registration.point('node.config').register_item(RedundantNodeRoleConfig)

from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import fields as registry_fields, registration


class Project(models.Model):
    """
    This class represents a project. Each project can contains some
    nodes and is also assigned a default IP allocation pool.
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    channel = models.IntegerField()
    ssid = models.CharField(max_length=50)
    ssid_backbone = models.CharField(max_length=50)
    ssid_mobile = models.CharField(max_length=50)
    captive_portal = models.BooleanField()
    sticker = models.CharField(max_length=50)

    # Geographical location
    geo_lat = models.FloatField(null=True)
    geo_long = models.FloatField(null=True)
    geo_zoom = models.IntegerField(null=True)

    # Pools linked to this project
    pools_core_ippool = models.ManyToManyField('core.IpPool', related_name='projects')

    def __unicode__(self):
        """
        Returns this project's name.
        """
        return self.name


def project_default(request=None):
    if request and hasattr(request.user, 'get_profile'):
        return request.user.get_profile().default_project
    else:
        projects = Project.objects.all()
        if projects.exists():
            return projects[0]
        else:
            return None


class ProjectConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes the project a node belongs to.
    """

    project = registry_fields.ModelSelectorKeyField(Project)

    class RegistryMeta:
        form_order = 2
        registry_id = 'core.project'
        registry_section = _("Project")
        registry_name = _("Basic Project")

registration.point('node.config').register_item(ProjectConfig)

from django import dispatch
from django.db import models, transaction
from django.db.models import signals as django_signals
from django.contrib.gis.db import models as gis_models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import fields as registry_fields, registration


class SSID(models.Model):
    """
    Network identitiy of a specific project.
    """

    project = models.ForeignKey('Project', related_name='ssids')
    purpose = models.CharField(max_length=50)
    default = models.BooleanField(default=False)
    bssid = registry_fields.MACAddressField(null=True, blank=True, verbose_name=_("BSSID"))
    essid = models.CharField(max_length=50, verbose_name=_("ESSID"))

    class Meta:
        verbose_name = 'SSID'

    def __unicode__(self):
        if self.bssid:
            return u'%s (%s)' % (self.essid, self.bssid)
        else:
            return self.essid


@dispatch.receiver(django_signals.post_save, sender=SSID)
def ssid_updated(sender, instance, **kwargs):
    """
    Ensure that only one SSID inside a project is selected as default.
    """

    if instance.default:
        SSID.objects.exclude(pk=instance.pk).filter(
            project=instance.project,
            default=True,
        ).update(default=False)


class Project(models.Model):
    """
    This class represents a project. Each project can contains some
    nodes and is also assigned a default IP allocation pool.
    """

    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    location = gis_models.PointField(null=True)

    # Pools linked to this project.
    ip_pools = models.ManyToManyField(
        'core.IpPool',
        related_name='projects',
        verbose_name=_("IP pools"),
        blank=True,
        # Only toplevel pools should be selected.
        limit_choices_to={'parent': None},
    )

    # Default pool.
    default_ip_pool = models.ForeignKey(
        'core.IpPool',
        related_name='+',
        verbose_name=_("Default IP pool"),
        null=True,
        blank=True,
        # Only toplevel pools should be selected.
        limit_choices_to={'parent': None},
    )

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.is_default:
            # Make sure other projects are not default.
            self.__class__.objects.filter(is_default=True).update(is_default=False)
        return super(Project, self).save(*args, **kwargs)


def project_default(request=None):
    if request and hasattr(request.user, 'profile') and request.user.profile.default_project is not None:
        return request.user.profile.default_project

    try:
        return Project.objects.get(is_default=True)
    except Project.DoesNotExist:
        projects = Project.objects.all()
        if projects.exists():
            return projects[0]
        else:
            return None


class ProjectConfig(registration.bases.NodeConfigRegistryItem):
    """
    Describes the project a node belongs to.
    """

    project = registry_fields.ModelRegistryChoiceField(Project)

    class RegistryMeta:
        form_weight = 2
        registry_id = 'core.project'
        registry_section = _("Project")
        registry_name = _("Basic Project")

registration.point('node.config').register_item(ProjectConfig)

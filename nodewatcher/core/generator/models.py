import requests

from django import dispatch
from django.contrib.auth import models as auth_models
from django.conf import settings
from django.core import exceptions as django_exceptions
from django.db.models import signals as django_signals
from django.db import models
from django.utils.translation import ugettext as _

from uuidfield import fields as uuid_field
import json_field

from .. import models as core_models
from . import connection, exceptions


class BuildChannel(models.Model):
    """
    Firmware build channel model, independent of any platform.
    """

    uuid = uuid_field.UUIDField(
        hyphenate=True, primary_key=True, auto=True,
        help_text=_('A unique build channel identifier.'),
    )
    name = models.CharField(
        max_length=20,
        unique=True,
        help_text=_('Human-readable build channel name.'),
    )
    description = models.TextField(
        blank=True,
        help_text=_('Optional build channel description.'),
    )
    builders = models.ManyToManyField(
        'Builder',
        related_name='channels',
        blank=True,
        help_text=_('Builders that can build this version.'),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when build channel was first registered.'),
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        help_text=_('Timestamp when build channel was last modified.'),
    )
    default = models.BooleanField(
        default=False,
        help_text=_('Use this build channel as default.'),
    )

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return u'<BuildChannel \'%s\'>' % self.name


@dispatch.receiver(django_signals.post_save, sender=BuildChannel)
def channel_updated(sender, instance, **kwargs):
    """
    Ensure that only one build channel is selected as default.
    """

    if instance.default:
        BuildChannel.objects.exclude(pk=instance.pk).filter(default=True).update(default=False)


class BuildVersion(models.Model):
    """
    Firmware build version.
    """

    uuid = uuid_field.UUIDField(
        hyphenate=True, primary_key=True, auto=True,
        help_text=_('A unique build version identifier.'),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when firmware version was first registered.'),
    )
    name = models.CharField(
        max_length=20,
        unique=True,
        help_text=_('Build version name.'),
    )

    def __unicode__(self):
        return self.name


class Builder(models.Model):
    """
    Firmware builder host configuration.
    """

    uuid = uuid_field.UUIDField(
        hyphenate=True, primary_key=True, auto=True,
        help_text=_('A unique builder identifier.'),
    )
    platform = models.CharField(
        max_length=50,
        blank=True,
        editable=False,
        help_text=_('Platform identifier.'),
    )
    architecture = models.CharField(
        max_length=50,
        blank=True,
        editable=False,
        help_text=_('Architecture identifier.'),
    )
    version = models.ForeignKey(
        BuildVersion,
        related_name='builders',
        blank=True,
        editable=False,
    )
    host = models.CharField(
        max_length=50,
        help_text=_('Builder host, reachable over SSH and HTTP.'),
    )
    private_key = models.TextField(
        help_text=_('Private key for SSH authentication.'),
    )

    class Meta:
        unique_together = ('platform', 'architecture', 'version')

    def get_metadata(self):
        """
        Establishes a connection with the builder and fetches metadata.

        :return: Builder metadata dictionary
        """

        return requests.get('http://%s/metadata' % self.host, timeout=5).json()

    def clean(self):
        """
        Automatically fetch builder information and construct a version
        when one does not yet exist.
        """

        # Fetch metadata via HTTP
        try:
            metadata = self.get_metadata()
            self.platform = str(metadata['platform'])
            self.architecture = str(metadata['architecture'])
            self.version, created = BuildVersion.objects.get_or_create(name=str(metadata['version']))
        except ValueError:
            raise django_exceptions.ValidationError(_('Failed to obtain metadata from builder!'))
        except requests.ConnectionError:
            raise django_exceptions.ValidationError(_('Failed to establish connection with builder!'))

        # Verify that the builder is also reachable over SSH
        try:
            with self.connect():
                pass
        except exceptions.BuilderConnectionFailed:
            raise django_exceptions.ValidationError(_('Failed to establish SSH connection with builder!'))
        except exceptions.MalformedPrivateKey:
            raise django_exceptions.ValidationError(_('Specified private key is malformed!'))

    def connect(self):
        """
        Establishes a connection with the builder via SSH and returns the
        connection controller.
        """

        return connection.BuilderConnection(self)

    def __unicode__(self):
        return self.host

    def __repr__(self):
        return u'<Builder \'%s\'>' % self.host


@dispatch.receiver(django_signals.post_delete, sender=Builder)
def builder_removed(sender, instance, **kwargs):
    """
    Remove a version without any builders left.
    """

    if not instance.version.builders.exists():
        instance.version.delete()


class BuildResult(models.Model):
    """
    Firmware build result.
    """

    # Build status choices
    PENDING = 'pending'
    BUILDING = 'building'
    FAILED = 'failed'
    OK = 'ok'
    STATUS_CHOICES = (
        (PENDING, _("pending")),
        (BUILDING, _("building")),
        (FAILED, _("failed")),
        (OK, _("ok")),
    )

    uuid = uuid_field.UUIDField(
        hyphenate=True, primary_key=True, auto=True,
        help_text=_('A unique build result identifier.'),
    )
    user = models.ForeignKey(
        auth_models.User,
        help_text=_('User that requested this firmware build.'),
    )
    node = models.ForeignKey(
        core_models.Node,
        help_text=_('Node this firmware build is for.'),
    )
    config = json_field.JSONField(
        blank=True,
        help_text=_('Configuration used to build this firmware.'),
    )
    build_channel = models.ForeignKey(
        BuildChannel,
        help_text=_('Firmware build channel used.'),
    )
    builder = models.ForeignKey(
        Builder,
        help_text=_('Firmware builder host used.'),
    )
    build_log = models.TextField(
        blank=True,
        null=True,
        help_text=_('Last lines of the build log.'),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when build result was created.'),
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        help_text=_('Timestamp when build result was last modified.'),
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text=_('Build status.')
    )

    def __repr__(self):
        return '<BuildResult for node \'%s\'>' % self.node_id


class BuildResultFile(models.Model):
    """
    A generated file belonging to a build result.
    """

    uuid = uuid_field.UUIDField(
        hyphenate=True, primary_key=True, auto=True,
        help_text=_('A unique build result file identifier.'),
    )
    result = models.ForeignKey(
        BuildResult,
        related_name='files',
    )
    file = models.FileField(
        upload_to=lambda r, filename: 'generator/%s/%s' % (r.result.uuid, filename),
        max_length=200,
    )

    def __repr__(self):
        return '<BuildResultFile for result \'%s\'>' % self.result_id

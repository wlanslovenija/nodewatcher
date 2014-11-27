from django.core import exceptions as django_exceptions
from django.contrib.auth import models as auth_models
from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import registration

from . import public_key, exceptions


class AuthenticationKey(models.Model):
    """
    An abstract authentication key.
    """

    name = models.CharField(
        max_length=100,
        help_text=_('Authentication key name.'),
    )
    fingerprint = models.TextField(
        editable=False,
        help_text=_('Public key fingerprint.'),
    )
    public_key = models.TextField(
        help_text=_('SSH encoded public key.'),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Timestamp when authentication key was first created.'),
    )

    class Meta:
        abstract = True

    def clean(self):
        """
        Validate the public key.
        """

        if not self.public_key:
            return
        self.public_key = self.public_key.strip()

        try:
            key = public_key.PublicKey(self.public_key)
        except exceptions.InvalidPublicKey:
            raise django_exceptions.ValidationError(_('Specified public key is malformed!'))

        self.fingerprint = key.get_fingerprint()

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.fingerprint)


class GlobalAuthenticationKey(AuthenticationKey):
    """
    Defines global (network-wide) authentication keys that should be added
    to all nodes.
    """

    enabled = models.BooleanField(
        default=True,
        help_text=_('Flag whether the authentication key should be enabled.'),
    )


class UserAuthenticationKey(AuthenticationKey):
    """
    Defines user-specific authentication keys that may be configured on nodes.
    """

    user = models.ForeignKey(auth_models.User, related_name='authentication_keys')


class PublicKeyAuthenticationConfig(cgm_models.AuthenticationConfig):
    """
    Public key authentication mechanism configuration.
    """

    public_key = models.ForeignKey(UserAuthenticationKey)

    class RegistryMeta(cgm_models.AuthenticationConfig.RegistryMeta):
        registry_name = _("Public Key")

registration.point('node.config').register_item(PublicKeyAuthenticationConfig)

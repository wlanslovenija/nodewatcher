from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import models as cgm_models
from nodewatcher.core.registry import registration


class PublicKeyAuthenticationConfig(cgm_models.AuthenticationConfig):
    """
    Public key authentication mechanism configuration.
    """

    public_key = models.TextField()

    class RegistryMeta(cgm_models.AuthenticationConfig.RegistryMeta):
        registry_name = _("Public Key")

registration.point('node.config').register_item(PublicKeyAuthenticationConfig)

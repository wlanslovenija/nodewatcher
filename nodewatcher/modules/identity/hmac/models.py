from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat import backends
from cryptography import exceptions

from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import registration
from nodewatcher.modules.identity.base import models as base_models

# Ensure default cryptography backend is loaded.
backends.default_backend()


class HmacIdentityConfig(base_models.IdentityMechanismConfig):
    """
    HMAC-based node identity verification mechanism configuration.
    """

    key = models.TextField()

    class RegistryMeta(base_models.IdentityMechanismConfig.RegistryMeta):
        registry_name = _("HMAC Signature")

    def is_match(self, data):
        """
        Returns true if the passed in public key matches this identity.
        """

        body = data['body']
        algorithm = data['algorithm']
        signature = data['signature']

        if not data['algorithm'] or not data['signature']:
            return False

        if algorithm == 'hmac-sha256':
            try:
                h = hmac.HMAC(self.key.encode('ascii'), hashes.SHA256(), backend=backends.default_backend())
                h.update(body)
                h.verify(signature)
                return True
            except exceptions.InvalidSignature:
                return False
        else:
            return False

    @classmethod
    def from_data(cls, data):
        """
        Returns constructor arguments for creating a new identity out of data.
        """

        # HMAC-based identity verification cannot be created from data.
        return None


registration.point('node.config').register_subitem(base_models.IdentityConfig, HmacIdentityConfig)

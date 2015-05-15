from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat import backends

from django.core import exceptions as django_exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import registration
from nodewatcher.modules.identity.base import models as base_models

# Ensure default cryptography backend is loaded.
backends.default_backend()


class PublicKeyIdentityConfig(base_models.IdentityMechanismConfig):
    """
    Public key node identity verification mechanism configuration.
    """

    public_key = models.TextField()

    class RegistryMeta(base_models.IdentityMechanismConfig.RegistryMeta):
        registry_name = _("Public Key")

    def clean(self):
        """
        Validate that the public key is correct.
        """

        try:
            key = self._extract_public_key(self.public_key.encode('ascii'))
            self.public_key = key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.PKCS1)
        except ValueError:
            raise django_exceptions.ValidationError({
                'public_key': _("Specified public key is not valid.")
            })

    @classmethod
    def _extract_public_key(cls, data):
        if data is None:
            raise ValueError("Invalid null public key.")

        backend = backends.default_backend()

        # First assume this is a public key.
        try:
            return serialization.load_pem_public_key(data, backend)
        except ValueError:
            # If it is not a public key, try to parse data as an X509 certificate.
            certificate = x509.load_pem_x509_certificate(data, backend)
            return certificate.public_key()

    def is_match(self, data):
        """
        Returns true if the passed in public key matches this identity.
        """

        # Extract public key from source data.
        try:
            key = self._extract_public_key(data)
        except ValueError:
            return False

        # Extract stored public key and compare.
        stored_key = self._extract_public_key(self.public_key.encode('ascii'))

        encoded_a = key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.PKCS1)
        encoded_b = stored_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.PKCS1)

        return encoded_a == encoded_b

    @classmethod
    def from_data(cls, data):
        """
        Returns constructor arguments for creating a new identity out of data.
        """

        try:
            key = cls._extract_public_key(data)
        except ValueError:
            return None

        return {
            'public_key': key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.PKCS1)
        }

registration.point('node.config').register_subitem(base_models.IdentityConfig, PublicKeyIdentityConfig)

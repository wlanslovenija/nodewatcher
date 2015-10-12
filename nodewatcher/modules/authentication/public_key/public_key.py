import hashlib

from cryptography import exceptions as cryptography_exceptions
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import serialization

from . import exceptions

# Ensure default cryptography backend is loaded.
backends.default_backend()


class PublicKey(object):
    """
    Public key parser.
    """

    def __init__(self, key):
        """
        Class constructor.

        :param key: Public key in SSH format
        """

        parts = key.split()
        if len(parts) != 2 and len(parts) != 3:
            raise exceptions.InvalidPublicKey

        # Validate that the public key is actually a valid key.
        try:
            self.key = serialization.load_ssh_public_key(key, backends.default_backend())
        except (cryptography_exceptions.UnsupportedAlgorithm, ValueError):
            raise exceptions.InvalidPublicKey

        # Decode raw key in order to compute the fingerprint in a compatible way.
        try:
            self.raw_key = parts[1].decode('base64')
        except Exception:
            raise exceptions.InvalidPublicKey

    def get_fingerprint(self):
        """
        Returns a hex-encoded MD5 fingerprint of the public key.
        """

        digest = hashlib.md5(self.raw_key).hexdigest()
        return ':'.join(a + b for a, b in zip(digest[::2], digest[1::2]))

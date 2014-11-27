import hashlib

from . import exceptions


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
        if len(parts) < 2 or len(parts) > 3:
            raise exceptions.InvalidPublicKey

        try:
            self.key = parts[1].decode('base64')
        except Exception:
            raise exceptions.InvalidPublicKey

    def get_fingerprint(self):
        """
        Returns a hex-encoded MD5 fingerprint of the public key.
        """

        digest = hashlib.md5(self.key).hexdigest()
        return ':'.join(a + b for a, b in zip(digest[::2], digest[1::2]))

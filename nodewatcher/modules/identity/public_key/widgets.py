import hashlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec

from django.template import loader as template_loader
from django.forms import widgets
from django.utils.translation import ugettext as _

from . import models


class PublicKeyWidget(widgets.Textarea):
    """
    A simple widget which renders the public key more nicely.
    """

    def format_fingerprint(self, hash_algorithm, value):
        """
        Formats a fingerprint for nicer display.

        :param hash_algorithm: Hash algorithm class
        :param value: Value to compute fingerprint on
        :return: Nicely formatted fingerprint
        """

        digest = hash_algorithm(value).hexdigest().upper()
        fingerprint = " ".join(('%s%s' % x for x in zip(digest[::2], digest[1::2])))
        return fingerprint

    def render(self, name, value, attrs=None):
        """
        Renders the widget.
        """

        context = {
            'name': name,
            'raw': value,
        }

        try:
            public_key = models.PublicKeyIdentityConfig._extract_public_key(value.encode('ascii'))
            valid = True
        except ValueError:
            public_key = None
            valid = False

        if public_key is not None:
            der = public_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.PKCS1)
            # TODO: Properly format fingerprints.
            context['fingerprint_sha256'] = self.format_fingerprint(hashlib.sha256, der)
            context['fingerprint_sha1'] = self.format_fingerprint(hashlib.sha1, der)

            if isinstance(public_key, rsa.RSAPublicKey):
                context['key_algorithm'] = 'RSA'
                context['key_size'] = public_key.key_size
            elif isinstance(public_key, dsa.DSAPublicKey):
                context['key_algorithm'] = 'DSA'
                context['key_size'] = public_key.key_size
            elif isinstance(public_key, ec.EllipticCurvePublicKey):
                context['key_algorithm'] = 'Elliptic Curve %s' % public_key.curve().name
                context['key_size'] = public_key.curve().key_size
            else:
                context['key_algorithm'] = _("Unknown")
                context['key_size'] = _("unknown")

        if valid:
            attrs['style'] = 'display: none'
        widget = super(PublicKeyWidget, self).render(name, value, attrs)

        if valid:
            return template_loader.render_to_string('identity/public_key/public_key.html', context) + widget
        else:
            return widget

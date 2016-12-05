from django import dispatch

from nodewatcher.modules.identity.base import signals, policy

from . import models


@dispatch.receiver(signals.verify)
def verify_hmac(sender, node, context, **kwargs):
    """
    Perform public key-based identity verification.
    """

    return policy.verify_identity(
        node,
        models.PublicKeyIdentityConfig,
        context.identity.certificate or None,
    )

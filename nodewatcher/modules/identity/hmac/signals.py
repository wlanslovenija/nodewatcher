from django import dispatch

from nodewatcher.modules.identity.base import signals, policy

from . import models


@dispatch.receiver(signals.verify)
def verify_hmac(sender, node, context, **kwargs):
    """
    Perform HMAC-based identity verification.
    """

    return policy.verify_identity(
        node,
        models.HmacIdentityConfig,
        {
            'body': context.push.data or '',
            'algorithm': context.identity.signature.algorithm or None,
            'signature': context.identity.signature.data or None,
        }
    )

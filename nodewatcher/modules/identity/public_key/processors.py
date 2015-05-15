from nodewatcher.core.monitor import processors as monitor_processors, exceptions
from nodewatcher.modules.identity.base import policy as identity_policy, events

from . import models as public_key_models


class VerifyNodePublicKey(monitor_processors.NodeProcessor):
    """
    A processor that verifies a node's public key against the known identities. In
    case verification fails, further processing of this node is aborted.

    The processor expects a PEM-encoded X509 certificate or public key to be
    present in 'context.identity.certificate'.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        # Perform node identity verification.
        verified = identity_policy.verify_identity(
            node,
            public_key_models.PublicKeyIdentityConfig,
            context.identity.certificate or None,
        )

        if not verified:
            # Create a warning for failed identity verification.
            events.IdentityVerificationFailed(node).post()
            raise exceptions.NodeProcessorAbort("Node identity verification failed.")
        else:
            events.IdentityVerificationFailed(node).absent()

        return context

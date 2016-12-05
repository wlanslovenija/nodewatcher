from nodewatcher.core.monitor import processors as monitor_processors, exceptions

from . import events, signals


class VerifyNodeIdentity(monitor_processors.NodeProcessor):
    """
    A processor that verifies a node's identity using the configured identity
    mechanisms. In case verification fails, further processing of this node is
    aborted.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        verifications = signals.verify.send(sender=self.__class__, node=node, context=context)
        if not any([x[1] for x in verifications]):
            # Create a warning for failed identity verification.
            events.IdentityVerificationFailed(node).post()
            raise exceptions.NodeProcessorAbort("Node identity verification failed.")
        else:
            events.IdentityVerificationFailed(node).absent()

        return context

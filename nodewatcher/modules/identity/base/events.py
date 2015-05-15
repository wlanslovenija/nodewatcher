from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.events import declarative as events, pool


class IdentityVerificationFailed(events.NodeWarningRecord):
    """
    Node identity verification failed.
    """

    description = _("Node identity verification has failed.")

    def __init__(self, node):
        """
        Class constructor.

        :param node: Node on which the event ocurred
        """

        super(IdentityVerificationFailed, self).__init__(
            [node],
            events.NodeWarningRecord.SEVERITY_ERROR,
        )

pool.register_record(IdentityVerificationFailed)

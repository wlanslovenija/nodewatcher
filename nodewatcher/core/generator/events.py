from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.events import declarative as events, pool


class BuildResultReady(events.NodeEventRecord):
    """
    Event emitted when a firmware generator build completes.
    """

    description = _("Firmware image version %(version)s has been built.")

    def __init__(self, build_result):
        """
        Class constructor.

        :param build_result: Build result instance
        """

        super(BuildResultReady, self).__init__(
            build_result.node,
            events.NodeEventRecord.SEVERITY_INFO,
            related_users=build_result.user,
            build_result=str(build_result.uuid),
            version=build_result.builder.version.name,
        )

pool.register_record(BuildResultReady)


class BuildResultFailed(events.NodeEventRecord):
    """
    Event emitted when a firmware generator build fails.
    """

    description = _("Generation of firmware version %(version)s has failed.")

    def __init__(self, build_result):
        """
        Class constructor.

        :param build_result: Build result instance
        """

        super(BuildResultReady, self).__init__(
            build_result.node,
            events.NodeEventRecord.SEVERITY_ERROR,
            related_users=build_result.user,
            build_result=str(build_result.uuid),
            version=build_result.builder.version.name,
        )

pool.register_record(BuildResultFailed)

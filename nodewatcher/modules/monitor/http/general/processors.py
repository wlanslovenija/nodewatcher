import datetime

from django.utils import timezone

from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors


class GeneralInfo(monitor_processors.NodeProcessor):
    """
    Stores general node info monitor data into the database. Will only run if HTTP
    monitor module has previously fetched data.
    """

    @monitor_processors.depends_on_context("http")
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        general = node.monitoring.core.general()
        if general is not None:
            general.uuid = None
            general.firmware = None

        version = context.http.get_module_version("core.general")
        if version == 0:
            # Unsupported version or data fetch failed (v0)
            if general:
                general.save()
            return context

        if general is None:
            general = node.monitoring.core.general(create=monitor_models.GeneralMonitor)

        if not general.first_seen:
            general.first_seen = timezone.now()

        general.last_seen = timezone.now()
        general.uuid = context.http.general.uuid
        general.firmware = context.http.general.version
        general.save()

        return context

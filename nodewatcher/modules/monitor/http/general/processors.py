import datetime

import pytz

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

        general = node.monitoring.core.general(create=monitor_models.CgmGeneralMonitor)
        general.uuid = context.http.general.uuid or None
        general.firmware = context.http.general.version or None
        general.save()

        return context

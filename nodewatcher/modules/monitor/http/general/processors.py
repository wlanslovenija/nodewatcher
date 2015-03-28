import datetime
import pytz

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

        version = context.http.get_module_version("core.general")
        if version == 0:
            # Unsupported version or data fetch failed (v0).
            return context

        # Create models when they don't yet exist.
        general = node.monitoring.core.general()
        if general is None:
            general = node.monitoring.core.general(create=monitor_models.GeneralMonitor)

        status = node.monitoring.system.status()
        if status is None:
            status = node.monitoring.system.status(create=monitor_models.SystemStatusMonitor)

        if not general.first_seen:
            general.first_seen = timezone.now()

        general.last_seen = timezone.now()
        if version >= 4:
            general.uuid = context.http.core.general.uuid
            general.firmware = context.http.core.general.version

            # Process node uptime and local time (v4+).
            status.uptime = int(context.http.core.general.uptime)
            local_time = int(context.http.core.general.local_time)
            status.local_time = datetime.datetime.fromtimestamp(local_time, pytz.utc)
        else:
            general.uuid = context.http.general.uuid
            general.firmware = context.http.general.version

            # Process node uptime and local time (v1+).
            uptime, _ = context.http.general.uptime.split()
            status.uptime = int(float(uptime))
            local_time = int(context.http.general.local_time)
            status.local_time = datetime.datetime.fromtimestamp(local_time, pytz.utc)

        general.save()
        status.save()

        return context

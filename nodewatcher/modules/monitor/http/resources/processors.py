import datetime

import pytz

from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors


class SystemStatus(monitor_processors.NodeProcessor):
    """
    Stores system status monitor data into the database. Will only run if HTTP
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
        if version >= 1:
            # Process node uptime and local time (v1+)
            uptime, _ = context.http.general.uptime.split()
            uptime = int(float(uptime))
            local_time = int(context.http.general.local_time)

            # Process general resources (v1+)
            loadavg = [float(x) for x in context.http.general.loadavg.split()[:3]]
            processes = int(context.http.general.loadavg.split()[3].split("/")[1])
        else:
            # Unsupported version (v0)
            return context

        if version == 1:
            # Process memory resources (v1)
            memory_free = int(context.http.general.memfree)
            memory_buffers = int(context.http.general.buffers)
            memory_cache = int(context.http.general.cached)
        elif version >= 2:
            # Process memory resources (v2+)
            memory_free = int(context.http.general.memory.free)
            memory_buffers = int(context.http.general.memory.buffers)
            memory_cache = int(context.http.general.memory.cache)
        else:
            assert False

        # Schema update for system status
        status = node.monitoring.system.status(create=monitor_models.SystemStatusMonitor)
        status.uptime = uptime
        status.local_time = datetime.datetime.fromtimestamp(local_time, pytz.utc)
        status.save()

        # Schema update for general resources
        resources = node.monitoring.system.resources.general(create=monitor_models.GeneralResourcesMonitor)
        resources.loadavg_1min = loadavg[0]
        resources.loadavg_5min = loadavg[1]
        resources.loadavg_15min = loadavg[2]
        resources.memory_free = memory_free
        resources.memory_buffers = memory_buffers
        resources.memory_cache = memory_cache
        resources.processes = processes
        resources.save()

        # Schema update for network resources
        if version >= 3:
            resources = node.monitoring.system.resources.network(create=monitor_models.NetworkResourcesMonitor)
            resources.routes = int(context.http.general.routes.ipv4) + int(context.http.general.routes.ipv6)
            resources.tcp_connections = int(context.http.general.connections.tcp)
            resources.udp_connections = int(context.http.general.connections.udp)
            resources.save()

        return context

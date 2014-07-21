
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

        gresources = node.monitoring.system.resources.general()
        if gresources is not None:
            gresources.loadavg_1min = None
            gresources.loadavg_5min = None
            gresources.loadavg_15min = None
            gresources.memory_free = None
            gresources.memory_buffers = None
            gresources.memory_cache = None
            gresources.processes = None

        nresources = node.monitoring.system.resources.network()
        if nresources is not None:
            nresources.routes = None
            nresources.tcp_connections = None
            nresources.udp_connections = None

        # In the old version, the "core.general" module reports resource usage, where
        # in the new one, this has been moved to its own "core.resources" module
        if context.http.get_version() == 3:
            version = context.http.get_module_version("core.resources")
        else:
            version = context.http.get_module_version("core.general")

        if version >= 2 and context.http.get_version() == 3:
            # Process general resources (v2+, new version)
            loadavg = [float(x) for x in context.http.core.resources.load_average]
            processes = sum(context.http.core.resources.processes.values())
        elif version >= 1:
            # Process general resources (v1+, old version)
            loadavg = [float(x) for x in context.http.general.loadavg.split()[:3]]
            processes = int(context.http.general.loadavg.split()[3].split("/")[1])
        else:
            # Unsupported version or data fetch failed (v0)
            if gresources:
                gresources.save()
            if nresources:
                nresources.save()
            return context

        # Create models when they don't exist
        if gresources is None:
            gresources = node.monitoring.system.resources.general(create=monitor_models.GeneralResourcesMonitor)

        if version >= 2 and context.http.get_version() == 3:
            # Process memory resources (v2+, new version)
            memory_free = int(context.http.core.resources.memory.free)
            memory_buffers = int(context.http.core.resources.memory.buffers)
            memory_cache = int(context.http.core.resources.memory.cache)
        elif version >= 2:
            # Process memory resources (v2+, old version)
            memory_free = int(context.http.general.memory.free)
            memory_buffers = int(context.http.general.memory.buffers)
            memory_cache = int(context.http.general.memory.cache)
        else:
            # Process memory resources (v1, old version)
            memory_free = int(context.http.general.memfree)
            memory_buffers = int(context.http.general.buffers)
            memory_cache = int(context.http.general.cached)

        # Schema update for general resources
        gresources.loadavg_1min = loadavg[0]
        gresources.loadavg_5min = loadavg[1]
        gresources.loadavg_15min = loadavg[2]
        gresources.memory_free = memory_free
        gresources.memory_buffers = memory_buffers
        gresources.memory_cache = memory_cache
        gresources.processes = processes
        gresources.save()

        # Schema update for network resources
        if version >= 3 or (version >= 2 and context.http.get_version() == 3):
            if nresources is None:
                nresources = node.monitoring.system.resources.network(create=monitor_models.NetworkResourcesMonitor)

            if context.http.get_version() == 3:
                # TODO: Number of routes is currently not yet reported
                nresources.tcp_connections = \
                    int(context.http.core.resources.connections.ipv4.tcp) + \
                    int(context.http.core.resources.connections.ipv6.tcp)

                nresources.udp_connections = \
                    int(context.http.core.resources.connections.ipv4.udp) + \
                    int(context.http.core.resources.connections.ipv6.udp)
            else:
                nresources.routes = int(context.http.general.routes.ipv4) + int(context.http.general.routes.ipv6)
                nresources.tcp_connections = int(context.http.general.connections.tcp)
                nresources.udp_connections = int(context.http.general.connections.udp)

            nresources.save()

        return context

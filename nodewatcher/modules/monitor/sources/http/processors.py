from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import processors as monitor_processors, events as monitor_events

from . import parser as telemetry_parser


class HTTPTelemetryContext(monitor_processors.ProcessorContext):
    """
    Augmented context for HTTP telemetry information that can be used
    by store/analyze modules for some common functionality like checking
    module presence/versions.
    """

    def get_version(self):
        """
        Returns the telemetry format version.
        """

        # Always return 0 when parsing has failed and no info is available
        if not self.get('successfully_parsed', False):
            return 0

        return self._meta.version

    def get_module_version(self, module):
        """
        Returns the active version of a telemetry module present on the remote
        node by checking the returned telemetry output.

        :param module: Module name (dot-separated namespace)
        :return: An integer representing the version or 0 if module is
          not installed/present
        """

        # Always return 0 when parsing has failed and no info is available
        if not self.get('successfully_parsed', False):
            return 0

        if self._meta.version == 2:
            module = module.replace('.', '-')
            metadata = self.META.modules.get(module)
            if metadata:
                try:
                    return int(metadata.serial)
                except ValueError:
                    # This could only happen when the parsed output is corrupted as serial
                    # should always be an integer
                    return 0
        elif self._meta.version == 3:
            try:
                return reduce(lambda x, y: x[y], module.split('.'), self)._meta.version
            except (KeyError, AttributeError):
                return 0

        return 0


class HTTPTelemetry(monitor_processors.NodeProcessor):
    """
    Implements fetching and parsing of nodewatcher HTTP telemetry data. It
    does not do any further processing, the processing must be done by
    individual modules in their store/analyze methods.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        if not context.push.source:
            # This processor is not being invoked from a push handler, check if the node is configured
            # for periodically polling telemetry and ignore it if it is not.
            telemetry_source = node.config.core.telemetry.http()
            if not telemetry_source or telemetry_source.source != 'poll':
                return context

            push = False
        else:
            context.node_available = True
            push = True

        node_available = context.node_available

        http_context = context.create('http', HTTPTelemetryContext)
        try:
            http_context.successfully_parsed = False

            # If the node is not marked as available, we should skip telemetry parsing
            if not node_available:
                return context

            if not push:
                router_id = node.config.core.routerid(queryset=True).get(rid_family='ipv4').router_id
                parser = telemetry_parser.HttpTelemetryParser(router_id, 80)
            else:
                parser = telemetry_parser.HttpTelemetryParser(data=context.push.data)

            # Fetch information from the router and merge it into local context
            try:
                parser.parse_into(http_context)
                if http_context._meta.version == 2:
                    # TODO: Add a warning that the node is using a legacy feed
                    pass
                http_context.successfully_parsed = True
                context.node_responds = True

                # Remove the warning if it is present.
                if hasattr(node.config.core.general(), 'router'):
                    monitor_events.TelemetryProcessingFailed(node, method='http').absent()
            except telemetry_parser.HttpTelemetryParseFailed:
                # If the node responded in some way, set the appropriate flag.
                if parser.node_responds:
                    context.node_responds = True

                # Create a warning in case the router has an associated firmware configuration.
                if hasattr(node.config.core.general(), 'router') and context.node_responds:
                    monitor_events.TelemetryProcessingFailed(node, method='http').post()
        except core_models.RouterIdConfig.DoesNotExist:
            # No router-id for this node can be found for IPv4; this means
            # that we have nothing to do here
            pass

        return context


class HTTPGetPushedNode(monitor_processors.NetworkProcessor):
    """
    A processor that populates the nodes set with the node that is set as the push
    source in the context.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors. Context is passed between network processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        if context.push.source:
            # Fetch a node based on the UUID set in the context and add it to the set.
            try:
                node = core_models.Node.objects.get(uuid=context.push.source)
                telemetry_source = node.config.core.telemetry.http()
                if telemetry_source.source != 'push':
                    # If the node is not configured to push, we ignore it.
                    return context, nodes

                nodes.add(node)
            except core_models.Node.DoesNotExist:
                self.logger.error("Node with UUID '%s' does not exist." % context.push.source)

        return context, nodes

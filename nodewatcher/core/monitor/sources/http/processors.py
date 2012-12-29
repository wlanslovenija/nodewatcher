from nodewatcher.core import models as core_models

from . import parser as telemetry_parser
from ... import processors as monitor_processors

class HTTPTelemetryContext(monitor_processors.ProcessorContext):
    """
    Augmented context for HTTP telemetry information that can be used
    by store/analyze modules for some common functionality like checking
    module presence/versions.
    """
    def get_module_version(self, module):
        """
        Returns the active version of a telemetry module present on the remote
        node by checking the returned telemetry output.

        :param module: Module name (dot-separated namespace)
        :return: An integer representing the version or 0 if module is
          not installed/present
        """
        module = module.replace('.', '-')
        metadata = self.META.modules.get(module)
        if metadata:
            try:
                return int(metadata.serial)
            except ValueError:
                # This could only happen when the parsed output is corrupted as serial
                # should always be an integer
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
        try:
            router_id = node.config.core.routerid(queryset = True).get(family = "ipv4").router_id
            parser = telemetry_parser.HttpTelemetryParser(router_id, 80)

            # Fetch information from the router and merge it into local context
            with context.in_namespace("http", HTTPTelemetryContext):
                try:
                    parser.parse_into(context)
                except telemetry_parser.HttpTelemetryParseFailed:
                    # Parsing has failed, log this; all components that did not get parsed
                    # will be missing from context and so depending modules will not process them
                    self.logger.error("Failed to parse HTTP telemetry feed from %s!" % router_id)
        except core_models.RouterIdConfig.DoesNotExist:
            # No router-id for this node can be found for IPv4; this means
            # that we have nothing to do here
            pass

        return context

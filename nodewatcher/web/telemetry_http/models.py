from web.core import models as core_models
from web.core.monitor import telemetry as monitor_telemetry
from . import parser as telemetry_parser

class HttpTelemetryModule(monitor_telemetry.TelemetryModule):
  """
  Implements fetching and parsing of nodewatcher HTTP telemetry data. It
  does not do any further processing, the processing must be done by
  individual modules in their store/analyze methods.
  """
  def fetch(self, context, node):
    """
    Fetches data from the node and parses it into internal format that is
    used for further processing.

    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    try:
      router_id = node.config.core.routerid(queryset = True).get(family = "ipv4").router_id
      parser = telemetry_parser.HttpTelemetryParser(router_id, 80)

      # Fetch information from the router and merge it into local context
      with context.in_namespace("http"):
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

monitor_telemetry.register_module(HttpTelemetryModule)

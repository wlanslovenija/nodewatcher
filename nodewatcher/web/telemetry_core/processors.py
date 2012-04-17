import datetime

from web.core import models as core_models
from web.core.monitor import processors as monitor_processors

class SystemStatusCheck(monitor_processors.NodeProcessor):
  """
  Stores system status telemetry data into the database. Will only run if HTTP
  telemetry module has previously fetched data.
  """
  @monitor_processors.depends_on_context("http")
  def process(self, context, node):
    """
    Called for every processed node.

    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    version = context.http.get_module_version("core.general")
    if version >= 1:
      # Process node uptime and local time
      uptime, _ = context.http.general.uptime.split()
      uptime = int(float(uptime))
      local_time = int(context.http.general.local_time)

      # Update the node's monitoring schema
      status = node.monitoring.system.status(create = core_models.SystemStatusMonitor)
      status.uptime = uptime
      status.local_time = datetime.datetime.fromtimestamp(local_time)
      status.save()

    return context

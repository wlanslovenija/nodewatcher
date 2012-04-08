import logging

from django.db import transaction

from web.core.monitor import processors

class TelemetryProcessor(processors.MonitoringProcessor):
  """
  Processor that fetches telemetry data from remote nodes and exposes it to
  modules in an internal nodewatcher format.
  """
  modules = []
  
  def process_first_pass(self, context, node):
    """
    Called for every processed node in the first pass. Should fetch and store
    data for the second pass.
    
    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    with context.in_namespace("telemetry"):
      for fetcher in self.modules:
        try:
          context = fetcher.fetch(context, node)
        except KeyboardInterrupt:
          raise
        except:
          self.report_exception("Telemetry module %s has failed with exception in fetch:" % \
                                fetcher.__class__.__name__)

      for storager in self.modules:
        try:
          sid = transaction.savepoint()
          context = storager.store(context, node)
          transaction.savepoint_commit(sid)
        except KeyboardInterrupt:
          transaction.savepoint_rollback(sid)
          raise
        except:
          transaction.savepoint_rollback(sid)
          self.report_exception("Telemetry module %s has failed with exception in store:" % \
                                storager.__class__.__name__)
    
    return context
  
  def process_second_pass(self, context, node):
    """
    Called for every processed node in the second pass. Should analyze the stored
    data but should not modify it in such a way to affect other analyzers (undefined
    results if it does).
    
    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    for analyzer in self.modules:
      try:
        sid = transaction.savepoint()
        context = analyzer.analyze(context, node)
        transaction.savepoint_commit(sid)
      except KeyboardInterrupt:
        transaction.savepoint_rollback(sid)
        raise
      except:
        transaction.savepoint_rollback(sid)
        self.report_exception("Telemetry module %s has failed with exception in analyze:" % \
                              analyzer.__class__.__name__)
    
    return context

processors.register_processor(TelemetryProcessor)

class TelemetryModule(object):
  """
  Nodewatcher telemetry processor module.
  """
  def __init__(self):
    """
    Class constructor.
    """
    self.logger = logging.getLogger("monitor.processor.telemetry.%s" % self.__class__.__name__)

  def fetch(self, context, node):
    """
    Fetches data from the node and parses it into internal format that is
    used for further processing.
    
    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    return context
  
  def store(self, context, node):
    """
    Retrieves data from nodewatcher telemetry and stores it into the monitoring
    schema.
    
    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    return context
  
  def analyze(self, context, node):
    """
    Analyzes node's monitoring data.
    
    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    return context

def register_module(module):
  """
  Registers a nodewatcher telemetry processing module.
  
  @param module: Module class
  """
  TelemetryProcessor.modules.append(module())
  return module


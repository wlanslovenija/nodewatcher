from web.core.monitor import processors

class NodewatcherTelemetryProcessor(processors.MonitoringProcessor):
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
      with context.in_namespace("nodewatcher"):
        for fetcher in self.modules:
          context = fetcher().fetch(context, node)
        
        for storager in self.modules:
          context = storager().store(context, node)
    
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
      context = analyzer().analyze(context, node)
    
    return context

processors.register_processor(NodewatcherTelemetryProcessor)

class NodewatcherTelemetryModule(object):
  """
  Nodewatcher telemetry processor module.
  """
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
  NodewatcherTelemetryProcessor.modules.append(module)
  return module


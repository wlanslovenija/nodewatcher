from web.core.monitor import processors

class MeasurementProcessor(processors.MonitoringProcessor):
  """
  Processor that invokes external measurements that are sourced on the host
  that is running the monitoring system.
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
    with context.in_namespace("measurements"):
      for measurement in self.modules:
        context = measurement().measure(context, node)
    
    return context

processors.register_processor(MeasurementProcessor)

class MeasurementModule(object):
  """
  Measurement module interface.
  """
  def measure(self, context, node):
    """
    Performs a measurement on a given node.
    
    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
    return context

def register_module(module):
  """
  Registers an external measurement module.
  
  @param module: Class implementing the MeasurementModule interface
  """
  MeasurementProcessor.modules.append(module)
  return module


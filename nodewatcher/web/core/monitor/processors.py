import contextlib

# Registered processors
processors = []

class ProcessorContext(dict):
  """
  A simple dictionary wrapper that supports automatic nesting
  of namespaces and attribute access.
  """
  def __init__(self):
    """
    Class constructor.
    """
    dict.__init__(self)
    self.__dict__['_namespace'] = []
  
  def __getitem__(self, key):
    """
    Dictionary access.
    """
    try:
      return dict.__getitem__(self, key)
    except KeyError:
      if key.startswith('_'):
        raise
      
      return dict.setdefault(self, key, ProcessorContext())
  
  def __getattr__(self, name):
    """
    Attribute access.
    """
    return reduce(lambda x, y: x[y], self._namespace, self)[name]
  
  def __setattr__(self, name, value):
    """
    Attribute update.
    """
    reduce(lambda x, y: x[y], self._namespace, self)[name] = value
  
  @contextlib.contextmanager
  def in_namespace(self, namespace):
    """
    Starts a new namespace.
    
    @param namespace: Namespace name
    """
    self._namespace.append(namespace)
    yield
    self._namespace.pop()

class MonitoringProcessor(object):
  """
  Interface for a monitoring processor.
  """
  def preprocess(self, context, nodes):
    """
    Invoked before processing specific nodes and should select the nodes
    that will be processed.
    
    @param context: Current context
    @param nodes: A list of nodes that are to be processed
    @return: A (possibly) modified context and a (possibly) filtered list of nodes
    """
    return context, nodes
  
  def postprocess(self, context, nodes):
    """
    Invoked after processing specific nodes.
    
    @param context: Current context
    @param nodes: A list of nodes that have been processed
    @return: A (possibly) modified context
    """
    return context
  
  def process_first_pass(self, context, node):
    """
    Called for every processed node in the first pass. Should fetch and store
    data for the second pass.
    
    @param context: Current context
    @param node: Node that is being processed
    @return: A (possibly) modified context
    """
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
    return context

def register_processor(processor):
  """
  Registers a new class to be a monitoring processor.
  
  @param processor: Class implementing the MonitoringProcessor interface
  """
  global processors
  processors.append(processor)


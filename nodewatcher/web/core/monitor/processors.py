import contextlib
import logging
import traceback

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
    Namespace-aware __getitem__.
    """
    if self._namespace:
      return self._ns().__getitem__(key)
    return self._get(key)

  def __setitem__(self, key, value):
    """
    Namespace-aware __setitem__.
    """
    if self._namespace:
      return self._ns().__setitem__(key, value)
    super(ProcessorContext, self).__setitem__(key, value)

  def _get(self, key):
    """
    Get that automatically creates ProcessorContexts when key doesn't exist.
    """
    try:
      return super(ProcessorContext, self).__getitem__(key)
    except KeyError:
      if key.startswith('_'):
        raise

      return super(ProcessorContext, self).setdefault(key, ProcessorContext())

  def __contains__(self, item):
    """
    Namespace-aware __contains__.
    """
    if self._namespace:
      return self._ns().__contains__(item)
    return super(ProcessorContext, self).__contains__(item)

  def _ns(self):
    """
    Namespace resolution.
    """
    return self._namespace[-1] if self._namespace else self

  def __getattr__(self, name):
    """
    Attribute access.
    """
    if name.startswith('_'):
      return super(ProcessorContext, self).__getattr__(name)
    return self[name]
  
  def __setattr__(self, name, value):
    """
    Attribute update.
    """
    if name.startswith('_'):
      return super(ProcessorContext, self).__setattr__(name, value)
    self[name] = value

  def setdefault(self, k, d=None):
    """
    Namespace-aware setdefault.
    """
    if self._namespace:
      return self._ns().setdefault(k, d)
    return super(ProcessorContext, self).setdefault(k, d)

  def merge_with(self, other):
    """
    Merges this dictionary with another (recursively).
    """
    for k, v in other.iteritems():
      if k in self:
        try:
          self[k] = self[k].merge_with(v)
        except AttributeError:
          self[k] = v
      else:
        self[k] = v
    
    return self
  
  @contextlib.contextmanager
  def in_namespace(self, namespace, ctx_class = None):
    """
    Starts a new namespace.
    
    @param namespace: Namespace name
    @param ctx_class: Optional context class to use for this namespace root (should
      be a subclass of `ProcessorContext`)
    """
    # Create a new instance
    ns = ctx_class() if ctx_class else ProcessorContext()
    self[namespace] = ns

    # Append to list of namespaces and enter the context
    self._namespace.append(ns)
    yield
    self._namespace.pop()

class MonitoringProcessor(object):
  """
  Interface for a monitoring processor.
  """
  def __init__(self):
    """
    Class constructor.
    """
    self.logger = logging.getLogger("monitor.processor.%s" % self.__class__.__name__)

  def report_exception(self, msg = "Processor has failed with exception:"):
    """
    Reports an exception via the built-in logger.

    @param msg: Message that should be included before the backtrace
    """
    if msg:
      self.logger.error(msg)
    self.logger.error(traceback.format_exc())

  def preprocess(self, context, nodes):
    """
    Invoked before processing specific nodes and should select the nodes
    that will be processed.
    
    @param context: Current context
    @param nodes: A set of nodes that are to be processed
    @return: A (possibly) modified context and a (possibly) modified set of nodes
    """
    return context, nodes
  
  def postprocess(self, context, nodes):
    """
    Invoked after processing specific nodes.
    
    @param context: Current context
    @param nodes: A set of nodes that have been processed
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
  processors.append(processor())

def depends_on_context(*keys):
  """
  A decorator that augments methods which receive context as a first
  argument and return a context. It ensures that the method is only called
  when certain keys are present in the method's context.
  """
  def decorator(f):
    def wrapper(self, context, *args, **kwargs):
      for key in keys:
        if key not in context:
          return context

      f(self, context, *args, **kwargs)

    return wrapper

  return decorator

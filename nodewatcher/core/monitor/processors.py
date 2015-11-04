import logging
import traceback

from nodewatcher.core import models as core_models


class ProcessorContext(dict):
    """
    A simple dictionary wrapper to support attribute access.
    """

    def __getitem__(self, key):
        """
        Get that automatically creates ProcessorContexts when key doesn't exist.
        """

        try:
            return super(ProcessorContext, self).__getitem__(key)
        except KeyError:
            if key.startswith('_'):
                raise

            return super(ProcessorContext, self).setdefault(key, ProcessorContext())

    def __getattr__(self, name):
        """
        Attribute access.
        """

        if name.startswith('_') and name not in self:
            return super(ProcessorContext, self).__getattribute__(name)
        return self[name]

    def __setattr__(self, name, value):
        """
        Attribute update.
        """

        if name.startswith('_'):
            return super(ProcessorContext, self).__setattr__(name, value)
        self[name] = value

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
                if isinstance(v, dict):
                    # Convert dictionaries to context instances.
                    context = ProcessorContext()
                    v = context.merge_with(v)

                self[k] = v

        return self

    def create(self, namespace, ctx_class=None):
        """
        Creates a new sub-context.

        :param namespace: Namespace
        :param ctx_class: Optional context class to use for this namespace root (should
          be a subclass of `ProcessorContext`)
        """

        if ctx_class is None:
            ctx_class = ProcessorContext

        ctx = self
        parts = namespace.split('.')
        for part in parts:
            ctx = ctx.setdefault(part, ctx_class())

        return ctx


class MonitoringProcessor(object):
    """
    Interface for a monitoring processor.
    """

    def __init__(self):
        """
        Class constructor.
        """

        self.logger = logging.getLogger('monitor.processor.%s' % self.__class__.__name__)

    def report_exception(self, msg="Processor has failed with exception:"):
        """
        Reports an exception via the built-in logger.

        :param msg: Message that should be included before the backtrace
        """

        if msg:
            self.logger.error(msg)
        self.logger.error(traceback.format_exc())


class NetworkProcessor(MonitoringProcessor):
    """
    Network processors are called with a set of nodes as a parameter and are run
    serially.
    """

    requires_transaction = True

    def __init__(self, worker_pool=None, **kwargs):
        """
        Class constructor.
        """

        super(NetworkProcessor, self).__init__(**kwargs)
        self._worker_pool = worker_pool

    def get_worker_pool(self):
        """
        Returns the worker pool instance for the run that is executing this network
        processor. It may be used to perform tasks in parallel.
        """

        return self._worker_pool

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors. Context is passed between network processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        return context, nodes


class NodeProcessor(MonitoringProcessor):
    """
    Node processors are called for each node in a worker process. They run in parallel
    for all nodes at once (depending on worker count). Context is discarded once
    all NodeProcessors for a specific node are run.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        return context

    def cleanup(self, context, node):
        """
        Called after all processors for a specific node have been called. Cleanup
        methods are called in reverse order.

        :param context: Current context
        :param node: Node that is being processed
        """

        pass


class GetAllNodes(NetworkProcessor):
    """
    A processor that populates the nodes set with all nodes currently present in the
    nodewatcher database.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors. Context is passed between network processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        for node in core_models.Node.objects.all():
            nodes.add(node)

        return context, nodes


def depends_on_context(key_name, key_type):
    """
    A decorator that augments methods which receive context as a first
    argument and return a context. It ensures that the method is only called
    when a key of a certain type exists in the context.
    """

    # Fail early if the second argument to isinstance is not a valid class/type.
    isinstance(None, key_type)

    def decorator(f):
        def wrapper(self, context, *args, **kwargs):
            if key_name in context and isinstance(context[key_name], key_type):
                return f(self, context, *args, **kwargs)

            return context

        return wrapper

    return decorator

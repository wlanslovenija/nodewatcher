from django import test

from nodewatcher.core import models as core_models

from . import processors


class ProcessorTestCase(test.TestCase):
    """
    Test case helper for testing monitoring processors.
    """

    def create_node(self):
        """
        Create a new test node.
        """

        node = core_models.Node()
        node.save()

        return node

    def run_processor(self, processor_class, node=None, context=None):
        """
        Runs a single processor.

        :param processor_class: Processor class
        :param node: Optional node instance for node processors
        :param context: Optional context dictionary
        """

        processor = processor_class()
        context = processors.ProcessorContext(context)

        if isinstance(processor, processors.NodeProcessor):
            try:
                processor.process(context, node)
            finally:
                processor.cleanup(context, node)
        else:
            # TODO: Implement support for testing network processors.
            raise NotImplementedError

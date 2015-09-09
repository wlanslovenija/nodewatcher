import collections

from . import base, exceptions


class StreamDescriptorPool(object):
    def __init__(self):
        """
        Class constructor.
        """

        self._descriptors = collections.OrderedDict()
        self._cache = {}

    def register(self, model, descriptor):
        """
        Registers a new stream descriptor.

        :param model: Underlying data model class
        :param descriptor: Descriptor class
        """

        if not issubclass(descriptor, base.StreamsBase):
            raise exceptions.StreamDescriptorHasInvalidBase("'%s' is not a subclass of nodewatcher.modules.datastream.base.StreamsBase" % descriptor.__name__)

        if model in self._descriptors:
            raise exceptions.StreamDescriptorAlreadyRegistered("A stream descriptor for model class '%s' is already registered" % model.__name__)

        self._descriptors[model] = descriptor

    def unregister(self, model):
        """
        Unregisters a stream descriptor.

        :param model: Underlying data model class
        """

        if model not in self._descriptors:
            raise exceptions.StreamDescriptorNotRegistered("Stream descriptor for model class '%s' is not registered" % model.__name__)

        del self._descriptors[model]

    def get_descriptor(self, model):
        """
        Returns a stream descriptor for a given model.

        :param model: Underlying data model instance
        """

        try:
            descriptor_class = self._descriptors[model.__class__]
            if (descriptor_class, model) not in self._cache:
                self._cache[(descriptor_class, model)] = descriptor_class(model)

            return self._cache[(descriptor_class, model)]
        except KeyError:
            raise exceptions.StreamDescriptorNotRegistered("Stream descriptor for model class '%s' is not registered" % model.__class__.__name__)

    def clear_descriptor(self, model):
        """
        Clears a cached stream descriptor for a given model.

        :param model: Underlying data model instance
        """

        try:
            descriptor_class = self._descriptors[model.__class__]
            if (descriptor_class, model) in self._cache:
                del self._cache[(descriptor_class, model)]
        except KeyError:
            raise exceptions.StreamDescriptorNotRegistered("Stream descriptor for model class '%s' is not registered" % model.__class__.__name__)

pool = StreamDescriptorPool()

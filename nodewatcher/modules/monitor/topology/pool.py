import collections
import copy

from nodewatcher.utils import loader

from . import exceptions


class TopologyAttributePool(object):
    def __init__(self):
        self._attributes = collections.OrderedDict()
        self._discovered = False
        self._states = []

    def __enter__(self):
        self._states.append((copy.copy(self._attributes), self._discovered))

    def __exit__(self, exc_type, exc_val, exc_tb):
        state = self._states.pop()

        if exc_type is not None:
            # Reset to the state before the exception so that future
            # calls do not raise FrontendComponentNotRegistered or
            # FrontendComponentAlreadyRegistered exceptions
            self._attributes, self._discovered = state

        # Re-raise any exception
        return False

    def discover_components(self):
        with self:
            if self._discovered:
                return
            self._discovered = True

            loader.load_modules('topology_storage')

    def register(self, attribute_or_iterable):
        from . import base

        if not hasattr(attribute_or_iterable, '__iter__'):
            attribute_or_iterable = [attribute_or_iterable]

        for attribute in attribute_or_iterable:
            if not isinstance(attribute, base.TopologyAttribute):
                raise exceptions.InvalidTopologyAttribute("'%s' is not a subclass of nodewatcher.modules.topology.base.TopologyAttribute" % attribute.__name__)

            attribute_name = attribute.get_name()

            if attribute_name in self._attributes.setdefault(attribute.get_self_lookup_key(), {}):
                raise exceptions.TopologyAttributeAlreadyRegistered("A topology attribute with name '%s' is already registered" % attribute_name)

            self._attributes[attribute.get_self_lookup_key()][attribute_name] = attribute

    def unregister(self, attribute_or_iterable):
        if not hasattr(attribute_or_iterable, '__iter__'):
            attribute_or_iterable = [attribute_or_iterable]

        for attribute in attribute_or_iterable:
            attribute_name = attribute.get_name()

            if attribute_name not in self._attributes:
                raise exceptions.TopologyAttributeNotRegistered("No topology attribute with name '%s' is registered" % attribute_name)

            del self._attributes[attribute_name]

    def get_all_attributes(self):
        self.discover_components()

        return self._attributes.values()

    def get_attributes(self, attribute_class, **kwargs):
        self.discover_components()

        try:
            return self._attributes[attribute_class.get_lookup_key(**kwargs)].values()
        except KeyError:
            return []

pool = TopologyAttributePool()

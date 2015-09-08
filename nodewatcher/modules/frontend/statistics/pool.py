import collections
import copy

from . import exceptions


class StatisticsResourcePool(object):
    def __init__(self):
        self._resources = collections.OrderedDict()
        self._states = []

    def __enter__(self):
        self._states.append((copy.copy(self._resources),))

    def __exit__(self, exc_type, exc_val, exc_tb):
        state = self._states.pop()

        if exc_type is not None:
            # Reset to the state before the exception so that future
            # calls do not raise FrontendComponentNotRegistered or
            # FrontendComponentAlreadyRegistered exceptions
            self._resources, = state

        # Re-raise any exception
        return False

    def register(self, resource_or_iterable):
        from . import resources

        if not hasattr(resource_or_iterable, '__iter__'):
            resource_or_iterable = [resource_or_iterable]

        for resource in resource_or_iterable:
            if not isinstance(resource, resources.StatisticsResource):
                raise exceptions.InvalidStatisticsResource("'%s' is not a subclass of nodewatcher.modules.frontend.statistics.resources.StatisticsResource" % resource.__name__)

            resource_name = resource.get_name()

            if resource_name in self._resources:
                raise exceptions.StatisticsResourceAlreadyRegistered("A statistics resource with name '%s' is already registered" % resource_name)

            self._resources[resource_name] = resource

    def unregister(self, resource_or_iterable):
        if not hasattr(resource_or_iterable, '__iter__'):
            resource_or_iterable = [resource_or_iterable]

        for resource in resource_or_iterable:
            resource_name = resource.get_name()

            if resource_name not in self._resources:
                raise exceptions.StatisticsResourceNotRegistered("No statistics resource with name '%s' is registered" % resource_name)

            del self._resources[resource_name]

    def get_all_resources(self):
        return self._resources.values()

    def get_resource(self, resource_name):
        try:
            return self._resources[resource_name]
        except KeyError:
            raise exceptions.StatisticsResourceNotRegistered("No statistics resource with name '%s' is registered" % resource_name)

pool = StatisticsResourcePool()

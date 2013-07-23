from django.conf import settings
from django.utils import importlib

from . import exceptions


class EventSinkPool(object):
    def __init__(self):
        """
        Class constructor.
        """

        self._sinks = {}
        self._discovered = False

    def _import_class(self, path, error_typ, error_msg):
        """
        A helper method for importing classes.
        """

        i = path.rfind(".")
        module, attr = path[:i], path[i + 1:]
        try:
            module = importlib.import_module(module)
            return getattr(module, attr)
        except (ImportError, AttributeError):
            raise error_typ(error_msg % path)

    def discover_sinks(self):
        """
        Discovers and loads all sinks.
        """

        from . import base

        if self._discovered:
            return
        self._discovered = True

        for name, descriptor in settings.EVENT_SINKS.items():
            sink = descriptor['sink']
            filters = descriptor.get('filters', [])

            # Attempt to import the sink class
            sink = self._import_class(sink, exceptions.EventSinkNotFound, "Error importing event sink %s!")
            if not issubclass(sink, base.EventSink):
                raise exceptions.InvalidEventSink("Event sink '%s' is not a subclass of nodewatcher.core.events.base.EventSink!")

            # Attempt to import any filters and register them on the sink
            sink = sink()
            for filter in filters:
                filter = self._import_class(filter, exceptions.EventFilterNotFound, "Error importing event filter %s!")
                sink.add_filter(filter())

            self._sinks[name] = sink

    def get_all_sinks(self):
        """
        Returns all the discovered sinks.
        """

        self.discover_sinks()

        return self._sinks.values()

    def get_sink(self, sink_name):
        """
        Returns the specified sink.

        :param sink_name: Name of the sink
        :return: Sink instance
        """

        self.discover_sinks()

        try:
            return self._sinks[sink_name]
        except KeyError:
            raise exceptions.EventSinkNotFound("Sink with name '%s' cannot be found!" % sink_name)

pool = EventSinkPool()

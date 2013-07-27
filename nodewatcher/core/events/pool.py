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

    def discover_sinks(self):
        """
        Discovers and loads all sinks.
        """

        from . import base

        if self._discovered:
            return
        self._discovered = True

        for app in settings.INSTALLED_APPS:
            try:
                importlib.import_module('.events', app)
            except ImportError, e:
                message = str(e)
                if message != 'No module named events':
                    raise

    def register(self, sink_or_iterable):
        """
        Registers new event sinks.

        :param sink_or_iterable: A valid sink class or a list of such classes
        """

        from . import base

        if not hasattr(sink_or_iterable, '__iter__'):
            sink_or_iterable = [sink_or_iterable]

        for sink in sink_or_iterable:
            if not issubclass(sink, base.EventSink):
                raise exceptions.InvalidEventSink("Event sink '%s' is not a subclass of nodewatcher.core.events.base.EventSink!" % sink.__name__)

            sink_name = sink.__name__

            if sink_name in self._sinks:
                raise exceptions.EventSinkAlreadyRegistered("Event sink with name '%s' is already registered" % sink_name)

            sink = sink()

            # Check if sink has been disabled by the settings
            sink_cfg = getattr(settings, 'EVENT_SINKS', {}).get(sink_name, {})
            if sink_cfg.get('disable', False) is True:
                sink.set_enabled(False)

            self._sinks[sink_name] = sink

    def unregister(self, sink_or_iterable):
        """
        Unregisters event sinks.

        :param sink_or_iterable: A valid sink class or a list of such classes
        """

        if not hasattr(sink_or_iterable, '__iter__'):
            sink_or_iterable = [sink_or_iterable]

        for sink in sink_or_iterable:
            sink_name = sink.__name__

            if sink_name not in self._sinks:
                raise exceptions.EventSinkNotRegistered("No event sink with name '%s' is registered" % sink_name)

            del self._sinks[sink_name]

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
            raise exceptions.EventSinkNotRegistered("No event sink with name '%s' is registered" % sink_name)

pool = EventSinkPool()

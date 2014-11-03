import copy
import re

from django.conf import settings

from ...utils import loader

from . import exceptions

VALID_NAME = re.compile('^[A-Za-z_][A-Za-z0-9_]*$')


class EventSinkPool(object):
    def __init__(self):
        """
        Class constructor.
        """

        self._sinks = {}
        self._records = {}
        self._discovered = False
        self._states = []

    def __enter__(self):
        self._states.append((copy.copy(self._sinks), copy.copy(self._records), self._discovered))

    def __exit__(self, exc_type, exc_val, exc_tb):
        state = self._states.pop()

        if exc_type is not None:
            # Reset to the state before the exception so that future
            # calls do not raise EventSinkNotRegistered or
            # EventSinkAlreadyRegistered exceptions
            self._sinks, self._records, self._discovered = state

        # Re-raise any exception
        return False

    def discover(self):
        """
        Discovers and loads all sinks and event records.
        """

        with self:
            if self._discovered:
                return
            self._discovered = True

            loader.load_modules('events')

    def register_sink(self, sink_or_iterable):
        """
        Registers new event sinks.

        :param sink_or_iterable: A valid sink class or a list of such classes
        """

        from . import base

        if not hasattr(sink_or_iterable, '__iter__'):
            sink_or_iterable = [sink_or_iterable]

        for sink in sink_or_iterable:
            if not issubclass(sink, base.EventSink):
                raise exceptions.InvalidEventSink("'%s' is not a subclass of nodewatcher.core.events.EventSink" % sink.__name__)

            sink_name = sink.get_name()

            if not VALID_NAME.match(sink_name):
                raise exceptions.InvalidEventSink("An evenk sink '%s' has invalid name" % sink_name)

            if sink_name in self._sinks:
                raise exceptions.EventSinkAlreadyRegistered("An event sink with name '%s' is already registered" % sink_name)

            # Pass sink configuration to the sink
            sink_cfg = getattr(settings, 'EVENT_SINKS', {}).get(sink_name, {})
            self._sinks[sink_name] = sink(**sink_cfg)

    def register_record(self, record_or_iterable):
        """
        Registers new event records.

        :param record_or_iterable: A valid event record class or a list of such classes
        """

        from . import declarative

        if not hasattr(record_or_iterable, '__iter__'):
            record_or_iterable = [record_or_iterable]

        for record in record_or_iterable:
            if not issubclass(record, declarative.NodeEventRecord):
                raise exceptions.InvalidEventRecord("'%s' is not a subclass of nodewatcher.core.events.declarative.NodeEventRecord" % record.__name__)

            if (record.source_name, record.source_type) in self._records:
                raise exceptions.EventRecordAlreadyRegistered("Event record class '%s' is already registered" % record.__name__)

            self._records[record.source_name, record.source_type] = record

    def unregister_sink(self, sink_or_iterable):
        """
        Unregisters event sinks.

        :param sink_or_iterable: A valid sink class or a list of such classes
        """

        if not hasattr(sink_or_iterable, '__iter__'):
            sink_or_iterable = [sink_or_iterable]

        for sink in sink_or_iterable:
            sink_name = sink.get_name()

            if sink_name not in self._sinks:
                raise exceptions.EventSinkNotRegistered("No event sink with name '%s' is registered" % sink_name)

            del self._sinks[sink_name]

    def get_all_sinks(self):
        """
        Returns all the discovered sinks.
        """

        self.discover()

        return self._sinks.values()

    def get_sink(self, sink_name):
        """
        Returns the specified sink.

        :param sink_name: Sink name
        :return: Sink instance
        """

        self.discover()

        try:
            return self._sinks[sink_name]
        except KeyError:
            raise exceptions.EventSinkNotRegistered("No event sink with name '%s' is registered" % sink_name)

    def get_record(self, source_name, source_type):
        """
        Returns the specified sink.

        :param source_name: Event record source name
        :param source_type: Event record source type
        :return: Event record class
        """

        self.discover()

        try:
            return self._records[source_name, source_type]
        except KeyError:
            raise exceptions.EventRecordNotRegistered("No event record with name '%s.%s' is registered" % (source_name, source_type))

    def has_sink(self, sink_name):
        return sink_name in self._sinks

pool = EventSinkPool()

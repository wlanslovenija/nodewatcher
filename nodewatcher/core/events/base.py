from django.utils import timezone

from . import exceptions
from .pool import pool

# Exports
__all__ = [
    'EventRecord',
    'EventFilter',
    'EventSink',
]


class EventRecord(object):
    """
    An event record.
    """

    def __init__(self, **kwargs):
        """
        Class constructor. Any keyword arguments are saved into the event record.
        """
        self.timestamp = timezone.now()
        self.__dict__.update(kwargs)

    def post(self):
        """
        Posts an event to subscribed sinks.
        """
        # Post event to sinks
        for sink in pool.get_all_sinks():
            sink.post(self)


class EventFilter(object):
    def filter(self, event):
        """
        Should decide whether to deliver the event or not.

        :param event: Event record
        :return: True if the event should be delivered, False otherwise
        """

        raise NotImplementedError


class EventSink(object):
    """
    Base class for sink implementations.
    """

    name = None

    def __init__(self, disable=False, **kwargs):
        """
        Class constructor.

        :param disable: Should the sink be disabled by default
        """

        self._enabled = not disable
        self._filters = []

    @classmethod
    def get_name(cls):
        """
        Returns the sink name.
        """

        if cls.name:
            return cls.name

        return cls.__name__

    def set_enabled(self, enabled):
        """
        Sets the enabled state of this sink.

        :param enabled: True for enabling the sink, False otherwise
        """

        self._enabled = enabled

    def add_filter(self, filter):
        """
        Adds a filter to this event sink.

        :param filter: Filter class to add
        """

        if not isinstance(filter, EventFilter):
            raise exceptions.InvalidEventFilter(
                "Event filter '%s' is not a subclass of nodewatcher.core.events.base.EventFilter!" % filter.__class__.__name__
            )

        self._filters.append(filter)

    def post(self, event):
        """
        Posts an event to this sink. The event might be filtered by any filters
        that are installed on this sink.

        :param event: Event record
        """

        if not self._enabled:
            return

        for filter in self._filters:
            if not filter.filter(event):
                return

        self.deliver(event)

    def deliver(self, event):
        """
        Should deliver the given event.

        :param event: Event record to deliver
        """

        raise NotImplementedError

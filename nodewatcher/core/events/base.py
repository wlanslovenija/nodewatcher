import copy

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
        Class constructor. Any keyword arguments are saved into the event record
        and must be JSON-serializable.
        """

        self.record = {
            'timestamp': timezone.now(),
        }
        self.record.update(kwargs)
        self._complement = False

    def __getattr__(self, key):
        try:
            return self.record[key]
        except KeyError:
            raise AttributeError(key)

    def __invert__(self):
        """
        Returns a complementary event (absence of an event).
        """

        clone = copy.copy(self)
        clone._complement = True
        return clone

    def is_absent(self):
        """
        Does this event record specify a complementary event (absence of an event).
        """

        return self._complement

    def post(self):
        """
        Posts an event to subscribed sinks.
        """

        for sink in pool.get_all_sinks():
            sink.post(self)

    def absent(self):
        """
        Posts the complementary event (absence of event) to subscribed sinks.
        """

        # Generate the complementary event.
        complement = ~self

        for sink in pool.get_all_sinks():
            sink.post(complement)

    def post_or_absent(self, condition):
        """
        Posts either the event (if the condition is True) or the complementary event
        (if the condition is False) based on the passed condition variable.

        :param condition: Condition variable
        """

        if condition:
            self.post()
        else:
            self.absent()


class EventFilter(object):
    """
    Base class for filter implementations.
    """

    name = None

    def __init__(self, disable=False, **kwargs):
        """
        Class constructor.

        :param disable: Should the filter be disabled by default
        """

        self._enabled = not disable

    @classmethod
    def get_name(cls):
        """
        Returns the filter name.
        """

        return cls.name or cls.__name__

    @property
    def enabled(self):
        """
        Returns true if this filter is enabled.
        """

        return self._enabled

    def set_enabled(self, enabled):
        """
        Sets the enabled state of this filter.

        :param enabled: True for enabling the filter, False otherwise
        """

        self._enabled = enabled

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

    def __init__(self, disable=False, filters=None, **kwargs):
        """
        Class constructor.

        :param disable: Should the sink be disabled by default
        """

        self._enabled = not disable
        self._filters = {}
        self._filter_cfg = filters or {}

    @classmethod
    def get_name(cls):
        """
        Returns the sink name.
        """

        return cls.name or cls.__name__

    def set_enabled(self, enabled):
        """
        Sets the enabled state of this sink.

        :param enabled: True for enabling the sink, False otherwise
        """

        self._enabled = enabled

    def add_filter(self, filter, **kwargs):
        """
        Adds a filter to this event sink. Any keyword arguments are passed to
        filter constructor and override any configured settings.

        :param filter: Filter class to add
        """

        try:
            if not issubclass(filter, EventFilter):
                raise TypeError
        except TypeError:
            raise exceptions.InvalidEventFilter(
                "Event filter '%s' is not a subclass of nodewatcher.core.events.base.EventFilter!" % filter.__class__.__name__
            )

        filter_name = filter.get_name()

        if filter_name in self._filters:
            raise exceptions.EventFilterAlreadyAttached(
                "Event filter '%s' is already attached to sink '%s'!" % (filter_name, self.get_name())
            )

        if 'disable' in kwargs:
            raise exceptions.FilterArgumentReserved("Event filter argument 'disable' cannot be overriden!")

        filter_cfg = self._filter_cfg.get(filter_name, {})
        filter_cfg.update(kwargs)
        self._filters[filter_name] = filter(**filter_cfg)

    def remove_filter(self, filter_name):
        """
        Removes an existing filter.

        :param filter_name: Name of the filter to remove
        """

        if filter_name not in self._filters:
            raise exceptions.EventFilterNotFound(
                "Event filter '%s' is not attached to sink '%s'!" % (filter_name, self.get_name())
            )

        del self._filters[filter_name]

    def post(self, event):
        """
        Posts an event to this sink. The event might be filtered by any filters
        that are installed on this sink.

        :param event: Event record
        """

        if not self._enabled:
            return

        for filter in self._filters.values():
            if filter.enabled and not filter.filter(event):
                return

        self.deliver(event)

    def deliver(self, event):
        """
        Should deliver the given event.

        :param event: Event record to deliver
        """

        raise NotImplementedError

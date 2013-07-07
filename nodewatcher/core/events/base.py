from django.utils import timezone

from . import exceptions
from .pool import pool

# Exports
__all__ = [
    'EventRecord',
    'EventFilter',
    'EventSink',
    'post',
]

class EventRecord(object):
    pass

class EventFilter(object):
    def filter(self, event):
        """
        Should decide whether to deliver the event or not.

        :param event: Event record
        :return: True if the event should be delivered, False otherwise
        """

        return True

class EventSink(object):
    def __init__(self):
        """
        Class constructor.
        """

        self._filters = []

    def add_filter(self, filter):
        """
        Adds a filter to this event sink.

        :param filter: Filter class to add
        """

        if not hasattr(filter, "filter"):
            raise exceptions.InvalidEventFilter("Filter must have a 'filter' method defined!")

        self._filters.append(filter)

    def post(self, event):
        """
        Posts an event to this sink. The event might be filtered by any filters
        that are installed on this sink.

        :param event: Event record
        """

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

def post(**kwargs):
    """
    Posts an event. Any keyword arguments are saved into the event record.
    """

    # Create an event record
    event = EventRecord()
    # TODO: Should we support registration of custom default attributes?
    event.timestamp = timezone.now()
    event.__dict__.update(kwargs)

    # Post event to all sinks
    for sink in pool.get_all_sinks():
        sink.post(event)

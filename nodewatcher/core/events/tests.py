from django.conf import settings
from django.utils import unittest
from django.test.utils import override_settings

from . import base, exceptions
from .pool import pool


class TestEventSink(base.EventSink):
    def __init__(self):
        super(TestEventSink, self).__init__()
        self.events = []

    def deliver(self, event):
        self.events.append(event)


class TestEventFilter(base.EventFilter):
    def filter(self, event):
        if getattr(event, 'c', None) is True:
            return False

        return True


class TestInvalidSubclass(object):
    pass


class EventsTestCase(unittest.TestCase):
    def setUp(self):
        # Setup a test sink
        pool.register(TestEventSink)
        pool.get_sink('TestEventSink').add_filter(TestEventFilter())
        # Fake discovery
        pool._discovered = True

    def tearDown(self):
        pool.unregister(TestEventSink)

    def test_event_processing(self):
        base.EventRecord(a=1, b=2, message="Hello event world!").post()
        base.EventRecord(a=3, b=4, message="Hello event world!").post()
        base.EventRecord(a=5, b=6, c=True, message="Hello event world!").post()
        base.EventRecord(a=7, b=8, message="Hello event world!").post()

        sink = pool.get_sink('TestEventSink')
        self.assertEqual(len(sink.events), 3)
        for x in sink.events:
            self.assertEqual(x.message, "Hello event world!")
        self.assertEqual(sink.events[0].a, 1)
        self.assertEqual(sink.events[0].b, 2)
        self.assertEqual(sink.events[1].a, 3)
        self.assertEqual(sink.events[1].b, 4)
        self.assertEqual(sink.events[2].a, 7)
        self.assertEqual(sink.events[2].b, 8)

    def test_exceptions(self):
        with self.assertRaises(exceptions.InvalidEventSink):
            pool.register(TestInvalidSubclass)

        with self.assertRaises(exceptions.InvalidEventFilter):
            pool.get_sink('TestEventSink').add_filter(TestEventFilter)

        with self.assertRaises(exceptions.InvalidEventFilter):
            pool.get_sink('TestEventSink').add_filter(TestInvalidSubclass())

        with self.assertRaises(exceptions.EventSinkAlreadyRegistered):
            pool.register(TestEventSink)

        with self.assertRaises(exceptions.EventSinkNotRegistered):
            pool.get_sink('NonExistantSink')


class EventsSettingsTestCase(unittest.TestCase):
    @override_settings(EVENT_SINKS={
        'TestEventSink': {
            'disable': True
        }
    })
    def test_settings(self):
        pool.register(TestEventSink)
        try:
            base.EventRecord(a=1, b=2, message="Hello event world!").post()
            sink = pool.get_sink('TestEventSink')
            self.assertEqual(len(sink.events), 0)
        finally:
            pool.unregister(TestEventSink)

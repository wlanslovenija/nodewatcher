from django.conf import settings
from django.utils import unittest

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
        if getattr(event, 'c', None) == True:
            return False

        return True

class TestInvalidSubclass(object):
    pass

class EventsTestCase(unittest.TestCase):
    def setUp(self):
        # Fake some sink configuration
        settings.EVENT_SINKS = {
            'test' : {
                'sink' : 'nodewatcher.core.events.tests.TestEventSink',
                'filters' : (
                    'nodewatcher.core.events.tests.TestEventFilter',
                )
            }
        }
        # Force re-discovery
        pool._discovered = False

    def test_event_processing(self):
        base.EventRecord(a=1, b=2, message="Hello event world!").post()
        base.EventRecord(a=3, b=4, message="Hello event world!").post()
        base.EventRecord(a=5, b=6, c=True, message="Hello event world!").post()
        base.EventRecord(a=7, b=8, message="Hello event world!").post()

        sink = pool.get_sink('test')
        self.assertEqual(len(sink.events), 3)
        for x in sink.events:
            self.assertEqual(x.message, "Hello event world!")
        self.assertEqual(sink.events[0].a, 1)
        self.assertEqual(sink.events[0].b, 2)
        self.assertEqual(sink.events[1].a, 3)
        self.assertEqual(sink.events[1].b, 4)
        self.assertEqual(sink.events[2].a, 7)
        self.assertEqual(sink.events[2].b, 8)

class InvalidEventsTestCase1(unittest.TestCase):
    def setUp(self):
        # Fake some invalid sink configuration
        settings.EVENT_SINKS = {
            'test' : {
                'sink' : 'nodewatcher.core.events.tests.TestEventSinkInvalid',
            }
        }
        # Force re-discovery
        pool._discovered = False

    def test_exceptions(self):
        with self.assertRaises(exceptions.EventSinkNotFound):
            base.EventRecord(a=1, b=2, message="Hello event world!").post()

class InvalidEventsTestCase2(unittest.TestCase):
    def setUp(self):
        # Fake some invalid sink configuration
        settings.EVENT_SINKS = {
            'test' : {
                'sink' : 'nodewatcher.core.events.tests.TestEventSink',
                'filters' : (
                    'this.is.an.invalid.filter.Spec',
                )
            }
        }
        # Force re-discovery
        pool._discovered = False

    def test_exceptions(self):
        with self.assertRaises(exceptions.EventFilterNotFound):
            base.EventRecord(a=1, b=2, message="Hello event world!").post()

class InvalidEventsTestCase3(unittest.TestCase):
    def setUp(self):
        # Fake some invalid sink configuration
        settings.EVENT_SINKS = {
            'test' : {
                'sink' : 'nodewatcher.core.events.tests.TestInvalidSubclass',
            }
        }
        # Force re-discovery
        pool._discovered = False

    def test_exceptions(self):
        with self.assertRaises(exceptions.InvalidEventSink):
            base.EventRecord(a=1, b=2, message="Hello event world!").post()


class InvalidEventsTestCase4(unittest.TestCase):
    def setUp(self):
        # Fake some invalid sink configuration
        settings.EVENT_SINKS = {
            'test' : {
                'sink' : 'nodewatcher.core.events.tests.TestEventSink',
                'filters' : (
                    'nodewatcher.core.events.tests.TestInvalidSubclass',
                )
            }
        }
        # Force re-discovery
        pool._discovered = False

    def test_exceptions(self):
        with self.assertRaises(exceptions.InvalidEventFilter):
            base.EventRecord(a=1, b=2, message="Hello event world!").post()

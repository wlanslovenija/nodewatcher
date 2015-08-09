from django import test as django_test
from django.conf import settings

import django_datastream

from . import base, exceptions, fields
from .pool import pool


class UnregisteredModel(object):
    pass


class DummyModel(object):
    uuid = None
    uptime = None
    topology = None


class InvalidBaseStreams(object):
    pass


class TestBaseStreams(base.StreamsBase):
    def get_stream_query_tags(self):
        return {'uuid': self._model.uuid}

    def get_stream_tags(self):
        return {'uuid': self._model.uuid}

    def get_stream_highest_granularity(self):
        return django_datastream.datastream.Granularity.Seconds


class TestStreams(TestBaseStreams):
    uptime = fields.IntegerField(tags={
        'title': "Uptime",
        'visualization': {
            'type': 'line',
            'initial_set': False,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    reboots = fields.ResetField("#uptime", tags={
        'title': "Reboots",
        'visualization': {
            'type': 'event',
            'initial_set': True,
            'with': {'uuid': fields.TagReference('uuid')},
        }
    })
    topology = fields.GraphField()


class RegistryTestCase(django_test.TestCase):
    def setUp(self):
        DATASTREAM_BACKEND_SETTINGS = settings.DATASTREAM_BACKEND_SETTINGS.copy()
        DATASTREAM_BACKEND_SETTINGS['database_name'] = 'test_nodewatcher_datastream'

        self.datastream = django_datastream.init_datastream(
            settings.DATASTREAM_BACKEND,
            DATASTREAM_BACKEND_SETTINGS,
        )

    def tearDown(self):
        pass

    def test_basic(self):
        # Register stream.
        pool.register(DummyModel, TestStreams)

        # Test invalid model without registered descriptor.
        with self.assertRaises(exceptions.StreamDescriptorNotRegistered):
            pool.get_descriptor(UnregisteredModel)

        # Test streams descriptor with invalid base.
        with self.assertRaises(exceptions.StreamDescriptorHasInvalidBase):
            pool.register(UnregisteredModel, InvalidBaseStreams)

        # Insert stuff into datastream.
        item = DummyModel()
        item.uuid = 1
        item.uptime = 1
        item.topology = {
            'v': [
                {'i': 'nodeA'},
                {'i': 'nodeB'},
                {'i': 'nodeC'},
            ],
            'e': [
                {'f': 'nodeA', 't': 'nodeB'},
                {'f': 'nodeB', 't': 'nodeC'},
                {'f': 'nodeC', 't': 'nodeA'},
            ]
        }

        descriptor = pool.get_descriptor(item)
        self.assertIsInstance(descriptor, TestStreams)

        # Test tag updates.
        self.assertEqual(descriptor.uptime.custom_tags['visualization']['initial_set'], False)
        descriptor.uptime.set_tags(visualization={'initial_set': True, 'foo': 1})
        self.assertEqual(descriptor.uptime.custom_tags['visualization']['initial_set'], True)
        self.assertEqual(descriptor.uptime.custom_tags['visualization']['foo'], 1)
        descriptor.uptime.reset_tags_to_default(visualization={'initial_set': True})
        self.assertEqual(descriptor.uptime.custom_tags['visualization']['initial_set'], False)
        self.assertEqual(descriptor.uptime.custom_tags['visualization']['foo'], 1)
        descriptor.uptime.reset_tags_to_default(visualization=True)
        self.assertNotIn('foo', descriptor.uptime.custom_tags['visualization'])
        self.assertEqual(descriptor.uptime.custom_tags['visualization']['initial_set'], False)

        descriptor.insert_to_stream(self.datastream)
        pool.clear_descriptor(item)

        # Unregister stream.
        pool.unregister(DummyModel)
        with self.assertRaises(exceptions.StreamDescriptorNotRegistered):
            pool.unregister(DummyModel)

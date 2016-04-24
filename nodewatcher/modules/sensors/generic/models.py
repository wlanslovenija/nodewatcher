from django import dispatch
from django.db import models
from django.utils.translation import gettext_noop

from nodewatcher.core.registry import registration
from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool


class GenericSensorMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Data storage for a generic sensor.
    """

    sensor_id = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=50)
    value = models.FloatField(null=True)

    class RegistryMeta:
        registry_id = 'sensors.generic'
        multiple = True

registration.point('node.monitoring').register_item(GenericSensorMonitor)


class GenericSensorMonitorStreams(ds_models.RegistryItemStreams):
    value = ds_fields.FloatField(tags={
        'title': ds_fields.TagReference('name', gettext_noop("%(name)s")),
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })

    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A dictionary of tags that uniquely identify this object
        """

        tags = super(GenericSensorMonitorStreams, self).get_stream_query_tags()
        tags.update({'sensor_id': self._model.sensor_id})
        return tags

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A dictionary of tags to include
        """

        tags = super(GenericSensorMonitorStreams, self).get_stream_tags()
        tags.update({
            'sensor_id': self._model.sensor_id,
            'name': self._model.name,
            'unit': self._model.unit,
        })
        return tags

ds_pool.register(GenericSensorMonitor, GenericSensorMonitorStreams)

# In case we have the frontend module installed, we also subscribe to its
# reset signal that gets called when a user requests a node's data to be reset.
try:
    from nodewatcher.modules.frontend.editor import signals as editor_signals

    @dispatch.receiver(editor_signals.reset_node)
    def sensors_node_reset(sender, request, node, **kwargs):
        """
        Remove all sensor data when a user requests the node to be reset.
        """

        node.monitoring.sensors.generic(queryset=True).delete()
except ImportError:
    pass

from django.db import models

from nodewatcher.core.registry import registration
from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool


class KoruzaMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    KORUZA reported data.
    """

    # Unit serial number.
    serial_number = models.CharField(max_length=50, null=True)
    # MCU connected state.
    mcu_connected = models.NullBooleanField()
    # Current motor coordinates.
    motor_x = models.IntegerField(null=True)
    motor_y = models.IntegerField(null=True)

    class RegistryMeta:
        registry_id = 'irnas.koruza'

registration.point('node.monitoring').register_item(KoruzaMonitor)


class KoruzaMonitorStreams(ds_models.RegistryItemStreams):
    motor_x = ds_fields.FloatField(tags={
        'title': 'KORUZA Motor X',
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    motor_y = ds_fields.FloatField(tags={
        'title': 'KORUZA Motor Y',
        'visualization': {
            'type': 'line',
            'initial_set': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })

ds_pool.register(KoruzaMonitor, KoruzaMonitorStreams)

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
    # Accelerometer data.
    accel_x_range1 = models.FloatField(null=True)
    accel_x_range1_maximum = models.FloatField(null=True)
    accel_x_range2 = models.FloatField(null=True)
    accel_x_range2_maximum = models.FloatField(null=True)
    accel_x_range3 = models.FloatField(null=True)
    accel_x_range3_maximum = models.FloatField(null=True)
    accel_x_range4 = models.FloatField(null=True)
    accel_x_range4_maximum = models.FloatField(null=True)

    accel_y_range1 = models.FloatField(null=True)
    accel_y_range1_maximum = models.FloatField(null=True)
    accel_y_range2 = models.FloatField(null=True)
    accel_y_range2_maximum = models.FloatField(null=True)
    accel_y_range3 = models.FloatField(null=True)
    accel_y_range3_maximum = models.FloatField(null=True)
    accel_y_range4 = models.FloatField(null=True)
    accel_y_range4_maximum = models.FloatField(null=True)

    accel_z_range1 = models.FloatField(null=True)
    accel_z_range1_maximum = models.FloatField(null=True)
    accel_z_range2 = models.FloatField(null=True)
    accel_z_range2_maximum = models.FloatField(null=True)
    accel_z_range3 = models.FloatField(null=True)
    accel_z_range3_maximum = models.FloatField(null=True)
    accel_z_range4 = models.FloatField(null=True)
    accel_z_range4_maximum = models.FloatField(null=True)

    class RegistryMeta:
        registry_id = 'irnas.koruza'

registration.point('node.monitoring').register_item(KoruzaMonitor)


class AccelerometerField(ds_fields.FloatField):
    def __init__(self, coordinate, range, maximum=False):
        maximum = ' Max' if maximum else ''
        super(AccelerometerField, self).__init__(
            tags={
                'title': 'KORUZA Accelerometer {}{} (R{})'.format(coordinate.capitalize(), maximum, range),
                'group': 'koruza_{}'.format(coordinate),
                'visualization': {
                    'with': {
                        'group': 'koruza_{}'.format(coordinate),
                        'node': ds_fields.TagReference('node'),
                    },
                    'type': 'line',
                    'initial_set': True,
                    'time_downsamplers': ['mean'],
                    'value_downsamplers': ['min', 'mean', 'max'],
                }
            }
        )


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

    accel_x_range1 = AccelerometerField('x', range=1)
    accel_x_range1_maximum = AccelerometerField('x', range=1, maximum=True)
    accel_x_range2 = AccelerometerField('x', range=2)
    accel_x_range2_maximum = AccelerometerField('x', range=2, maximum=True)
    accel_x_range3 = AccelerometerField('x', range=3)
    accel_x_range3_maximum = AccelerometerField('x', range=3, maximum=True)
    accel_x_range4 = AccelerometerField('x', range=4)
    accel_x_range4_maximum = AccelerometerField('x', range=4, maximum=True)

    accel_y_range1 = AccelerometerField('y', range=1)
    accel_y_range1_maximum = AccelerometerField('y', range=1, maximum=True)
    accel_y_range2 = AccelerometerField('y', range=2)
    accel_y_range2_maximum = AccelerometerField('y', range=2, maximum=True)
    accel_y_range3 = AccelerometerField('y', range=3)
    accel_y_range3_maximum = AccelerometerField('y', range=3, maximum=True)
    accel_y_range4 = AccelerometerField('y', range=4)
    accel_y_range4_maximum = AccelerometerField('y', range=4, maximum=True)

    accel_z_range1 = AccelerometerField('z', range=1)
    accel_z_range1_maximum = AccelerometerField('z', range=1, maximum=True)
    accel_z_range2 = AccelerometerField('z', range=2)
    accel_z_range2_maximum = AccelerometerField('z', range=2, maximum=True)
    accel_z_range3 = AccelerometerField('z', range=3)
    accel_z_range3_maximum = AccelerometerField('z', range=3, maximum=True)
    accel_z_range4 = AccelerometerField('z', range=4)
    accel_z_range4_maximum = AccelerometerField('z', range=4, maximum=True)

ds_pool.register(KoruzaMonitor, KoruzaMonitorStreams)

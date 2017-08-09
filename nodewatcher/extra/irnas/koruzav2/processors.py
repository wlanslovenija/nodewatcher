from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.modules.monitor.sources.http import processors as http_processors

from . import models


class Koruza(monitor_processors.NodeProcessor):
    """
    Stores KORUZA monitor data into the database. Will only run if HTTP
    monitor module has previously fetched data.
    """

    ACCELEROMETER_COORDINATES = ('x', 'y', 'z')
    ACCELEROMETER_RANGES = 4

    @monitor_processors.depends_on_context('http', http_processors.HTTPTelemetryContext)
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        version = context.http.get_module_version('irnas.koruza')

        if version >= 1:
            koruza = node.monitoring.irnas.koruza(create=models.KoruzaMonitor)
            status = context.http.irnas.koruza.status
            if status.serial_number:
                koruza.serial_number = str(status.serial_number)
            koruza.mcu_connected = bool(status.connected)
            koruza.motor_x = int(status.motors.x)
            koruza.motor_y = int(status.motors.y)

            for coordinate in self.ACCELEROMETER_COORDINATES:
                for f_range in range(self.ACCELEROMETER_RANGES):
                    if status.accelerometer and status.accelerometer.connected:
                        values = status.accelerometer[coordinate]
                        average = values[f_range]['average']
                        maximum = values[f_range]['maximum']
                    else:
                        average = None
                        maximum = None

                    setattr(koruza, 'accel_{}_range{}'.format(coordinate, f_range + 1), average)
                    setattr(koruza, 'accel_{}_range{}_maximum'.format(coordinate, f_range + 1), maximum)

            koruza.save()

            # Automatically configure reported static Router ID.
            if status.network.ip_address:
                rid, created = core_models.StaticIpRouterIdConfig.objects.get_or_create(
                    root=node,
                    address='{}/32'.format(status.network.ip_address),
                )

                if created:
                    core_models.StaticIpRouterIdConfig.objects.filter(root=node).exclude(pk=rid.pk).delete()

        return context

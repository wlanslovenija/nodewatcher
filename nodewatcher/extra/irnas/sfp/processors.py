import math

from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.modules.monitor.sources.http import processors as http_processors


class SFP(monitor_processors.NodeProcessor):
    """
    Stores SFP monitor data into the database. Will only run if HTTP
    monitor module has previously fetched data.
    """

    MEASUREMENTS = ('temperature', 'vcc', 'tx_bias', 'tx_power', 'rx_power', 'rx_power_dbm')
    STATISTICS = ('variance', 'minimum', 'maximum')

    def get_rx_power_dbm_value(self, data, statistic):
        """
        Convert RX power to dBm.
        """

        if not data:
            return None

        try:
            rx_power = float(data.rx_power[statistic])
            rx_power_dbm = 10 * math.log10(rx_power)
            if rx_power_dbm < -40:
                rx_power_dbm = -40
        except ValueError:
            rx_power_dbm = -40

        return rx_power_dbm

    @monitor_processors.depends_on_context("http", http_processors.HTTPTelemetryContext)
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        version = context.http.get_module_version('irnas.sfp')

        existing_sfps = {}
        for sfp in node.monitoring.irnas.sfp():
            # Clear measurements.
            for measurement in self.MEASUREMENTS:
                setattr(sfp, measurement, None)

            existing_sfps[sfp.serial_number] = sfp

        if version >= 1:
            for serial_number, data in context.http.irnas.sfp.modules.items():
                statistics = context.http.irnas.sfp.statistics[serial_number]

                defaults = {
                    'bus': str(data.bus),
                    'manufacturer': str(data.manufacturer),
                    'revision': str(data.revision),
                    'type': int(data.type),
                    'connector': int(data.connector),
                    'bitrate': int(data.bitrate),
                    'wavelength': int(data.wavelength),
                }

                for measurement in self.MEASUREMENTS:
                    get_value = getattr(
                        self,
                        'get_{}_value'.format(measurement),
                        lambda data, statistic: float(data[measurement][statistic]) if data else None
                    )

                    defaults[measurement] = get_value(statistics, 'average')

                    for statistic in self.STATISTICS:
                        defaults['{}_{}'.format(measurement, statistic)] = get_value(statistics, statistic)

                node.monitoring.irnas.sfp(queryset=True).update_or_create(
                    root=node,
                    serial_number=serial_number,
                    defaults=defaults,
                )

                if serial_number in existing_sfps:
                    del existing_sfps[serial_number]

        for sfp in existing_sfps.values():
            sfp.save()

        return context

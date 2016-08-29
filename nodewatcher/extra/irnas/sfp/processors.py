from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.modules.monitor.sources.http import processors as http_processors


class SFP(monitor_processors.NodeProcessor):
    """
    Stores SFP monitor data into the database. Will only run if HTTP
    monitor module has previously fetched data.
    """

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
            sfp.temperature = None
            sfp.vcc = None
            sfp.tx_bias = None
            sfp.tx_power = None
            sfp.rx_power = None
            existing_sfps[sfp.serial_number] = sfp

        if version >= 1:
            for serial_number, data in context.http.irnas.sfp.modules.items():
                diagnostics = context.http.irnas.sfp.diagnostics[serial_number].value

                node.monitoring.irnas.sfp(queryset=True).update_or_create(
                    root=node,
                    serial_number=serial_number,
                    defaults={
                        'bus': str(data.bus),
                        'manufacturer': str(data.manufacturer),
                        'revision': str(data.revision),
                        'type': int(data.type),
                        'connector': int(data.connector),
                        'bitrate': int(data.bitrate),
                        'wavelength': int(data.wavelength),
                        # Diagnostics.
                        'temperature': float(diagnostics.temperature) if diagnostics else None,
                        'vcc': float(diagnostics.vcc) if diagnostics else None,
                        'tx_bias': float(diagnostics.tx_bias) if diagnostics else None,
                        'tx_power': float(diagnostics.tx_power) if diagnostics else None,
                        'rx_power': float(diagnostics.rx_power) if diagnostics else None,
                    }
                )

                if serial_number in existing_sfps:
                    del existing_sfps[serial_number]

        for sfp in existing_sfps.values():
            sfp.save()

        return context

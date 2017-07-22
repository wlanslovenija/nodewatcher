from nodewatcher.core.monitor import test
from nodewatcher.modules.monitor.sources.http import processors as http_processors

from . import processors as koruza_processors


class KoruzaProcessorTestCase(test.ProcessorTestCase):
    def generate_context(self, ip_address):
        """
        Generate test context for the processor.

        :param ip_address: Unit IP address
        """
        return {
            'http': http_processors.HTTPTelemetryContext({
                'successfully_parsed': True,
                '_meta': {
                    'version': 3,
                },
                'irnas': {
                    'koruza': {
                        '_meta': {
                            'version': 1,
                        },
                        'status': {
                            'serial_number': '0001',
                            'connected': True,
                            'motors': {
                                'x': 1000,
                                'y': 2000,
                            },
                            'network': {
                                'ip_address': ip_address,
                            },
                        }
                    }
                }
            })
        }

    def test_measurements(self):
        node = self.create_node()

        self.run_processor(
            koruza_processors.Koruza,
            node=node,
            context=self.generate_context('192.168.42.42')
        )

        koruza = node.monitoring.irnas.koruza()
        self.assertEqual(koruza.serial_number, '0001')
        self.assertEqual(koruza.mcu_connected, True)
        self.assertEqual(koruza.motor_x, 1000)
        self.assertEqual(koruza.motor_y, 2000)

    def test_router_ids(self):
        node = self.create_node()

        self.run_processor(
            koruza_processors.Koruza,
            node=node,
            context=self.generate_context('192.168.42.42')
        )

        router_ids = node.config.core.routerid()
        self.assertEqual(len(router_ids), 1)
        self.assertEqual(router_ids[0].router_id, '192.168.42.42')

        # Process again and check that router ID is correctly updated.
        self.run_processor(
            koruza_processors.Koruza,
            node=node,
            context=self.generate_context('192.168.42.42')
        )

        router_ids = node.config.core.routerid()
        self.assertEqual(len(router_ids), 1)
        self.assertEqual(router_ids[0].router_id, '192.168.42.42')

        # Change router ID and check that it works.
        self.run_processor(
            koruza_processors.Koruza,
            node=node,
            context=self.generate_context('192.168.42.43')
        )

        router_ids = node.config.core.routerid()
        self.assertEqual(len(router_ids), 1)
        self.assertEqual(router_ids[0].router_id, '192.168.42.43')

from nodewatcher.core.monitor import test
from nodewatcher.modules.monitor.sources.http import processors as http_processors

from . import processors as koruza_processors


class KoruzaProcessorTestCase(test.ProcessorTestCase):
    def generate_context(self, ip_address, accelerometer=True):
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
                                'connected': True,
                                'x': 1000,
                                'y': 2000,
                            },
                            'accelerometer': {
                                'connected': accelerometer,
                                'x': [
                                    {
                                        'average': 10.0,
                                        'count': 120,
                                        'variance': 100.0,
                                        'maximum': 100,
                                    },
                                    {
                                        'average': 20.0,
                                        'count': 120,
                                        'variance': 200.0,
                                        'maximum': 200,
                                    },
                                    {
                                        'average': 30.0,
                                        'count': 120,
                                        'variance': 300.0,
                                        'maximum': 300,
                                    },
                                    {
                                        'average': 40.0,
                                        'count': 120,
                                        'variance': 400.0,
                                        'maximum': 400,
                                    },
                                ],
                                'y': [
                                    {
                                        'average': 10.0,
                                        'count': 120,
                                        'variance': 100.0,
                                        'maximum': 100,
                                    },
                                    {
                                        'average': 20.0,
                                        'count': 120,
                                        'variance': 200.0,
                                        'maximum': 200,
                                    },
                                    {
                                        'average': 30.0,
                                        'count': 120,
                                        'variance': 300.0,
                                        'maximum': 300,
                                    },
                                    {
                                        'average': 40.0,
                                        'count': 120,
                                        'variance': 400.0,
                                        'maximum': 400,
                                    },
                                ],
                                'z': [
                                    {
                                        'average': 10.0,
                                        'count': 120,
                                        'variance': 100.0,
                                        'maximum': 100,
                                    },
                                    {
                                        'average': 20.0,
                                        'count': 120,
                                        'variance': 200.0,
                                        'maximum': 200,
                                    },
                                    {
                                        'average': 30.0,
                                        'count': 120,
                                        'variance': 300.0,
                                        'maximum': 300,
                                    },
                                    {
                                        'average': 40.0,
                                        'count': 120,
                                        'variance': 400.0,
                                        'maximum': 400,
                                    },
                                ]
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

        self.assertEqual(koruza.accel_x_range1, 10)
        self.assertEqual(koruza.accel_x_range1_maximum, 100)
        self.assertEqual(koruza.accel_x_range2, 20)
        self.assertEqual(koruza.accel_x_range2_maximum, 200)
        self.assertEqual(koruza.accel_x_range3, 30)
        self.assertEqual(koruza.accel_x_range3_maximum, 300)
        self.assertEqual(koruza.accel_x_range4, 40)
        self.assertEqual(koruza.accel_x_range4_maximum, 400)

        self.assertEqual(koruza.accel_y_range1, 10)
        self.assertEqual(koruza.accel_y_range1_maximum, 100)
        self.assertEqual(koruza.accel_y_range2, 20)
        self.assertEqual(koruza.accel_y_range2_maximum, 200)
        self.assertEqual(koruza.accel_y_range3, 30)
        self.assertEqual(koruza.accel_y_range3_maximum, 300)
        self.assertEqual(koruza.accel_y_range4, 40)
        self.assertEqual(koruza.accel_y_range4_maximum, 400)

        self.assertEqual(koruza.accel_z_range1, 10)
        self.assertEqual(koruza.accel_z_range1_maximum, 100)
        self.assertEqual(koruza.accel_z_range2, 20)
        self.assertEqual(koruza.accel_z_range2_maximum, 200)
        self.assertEqual(koruza.accel_z_range3, 30)
        self.assertEqual(koruza.accel_z_range3_maximum, 300)
        self.assertEqual(koruza.accel_z_range4, 40)
        self.assertEqual(koruza.accel_z_range4_maximum, 400)

        # Disconnect accelerometer.
        self.run_processor(
            koruza_processors.Koruza,
            node=node,
            context=self.generate_context('192.168.42.42', accelerometer=False)
        )

        koruza = node.monitoring.irnas.koruza()
        self.assertEqual(koruza.accel_x_range1, None)
        self.assertEqual(koruza.accel_x_range1_maximum, None)
        self.assertEqual(koruza.accel_x_range2, None)
        self.assertEqual(koruza.accel_x_range2_maximum, None)
        self.assertEqual(koruza.accel_x_range3, None)
        self.assertEqual(koruza.accel_x_range3_maximum, None)
        self.assertEqual(koruza.accel_x_range4, None)
        self.assertEqual(koruza.accel_x_range4_maximum, None)

        self.assertEqual(koruza.accel_y_range1, None)
        self.assertEqual(koruza.accel_y_range1_maximum, None)
        self.assertEqual(koruza.accel_y_range2, None)
        self.assertEqual(koruza.accel_y_range2_maximum, None)
        self.assertEqual(koruza.accel_y_range3, None)
        self.assertEqual(koruza.accel_y_range3_maximum, None)
        self.assertEqual(koruza.accel_y_range4, None)
        self.assertEqual(koruza.accel_y_range4_maximum, None)

        self.assertEqual(koruza.accel_z_range1, None)
        self.assertEqual(koruza.accel_z_range1_maximum, None)
        self.assertEqual(koruza.accel_z_range2, None)
        self.assertEqual(koruza.accel_z_range2_maximum, None)
        self.assertEqual(koruza.accel_z_range3, None)
        self.assertEqual(koruza.accel_z_range3_maximum, None)
        self.assertEqual(koruza.accel_z_range4, None)
        self.assertEqual(koruza.accel_z_range4_maximum, None)

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

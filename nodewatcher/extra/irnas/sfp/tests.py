from nodewatcher.core.monitor import test
from nodewatcher.modules.monitor.sources.http import processors as http_processors

from . import processors as sfp_processors


class SfpProcessorTestCase(test.ProcessorTestCase):
    def generate_context(self):
        """
        Generate test context for the processor.
        """
        return {
            'http': http_processors.HTTPTelemetryContext({
                'successfully_parsed': True,
                '_meta': {
                    'version': 3,
                },
                'irnas': {
                    'sfp': {
                        '_meta': {
                            'version': 1,
                        },
                        'modules': {
                            'H800S003984': {
                                'bus': '/dev/i2c-1',
                                'manufacturer': 'OEM',
                                'revision': '1.0',
                                'serial_number': 'H800S003984',
                                'type': 3,
                                'connector': 7,
                                'bitrate': 1300,
                                'wavelength': 1310
                            }
                        },
                        'diagnostics': {
                            'H800S003984': {
                                'value': {
                                    'temperature': '46.7344',
                                    'vcc': '3.1691',
                                    'tx_bias': '18.8240',
                                    'tx_power': '0.6180',
                                    'rx_power': '0.0000'
                                },
                                'error_upper': {
                                    'temperature': '95.0000',
                                    'vcc': '3.5600',
                                    'tx_bias': '80.0000',
                                    'tx_power': '1.5849',
                                    'rx_power': '0.6310'
                                },
                                'error_lower': {
                                    'temperature': '-40.0000',
                                    'vcc': '3.0400',
                                    'tx_bias': '2.0000',
                                    'tx_power': '0.1995',
                                    'rx_power': '0.0032'
                                },
                                'warning_upper': {
                                    'temperature': '90.0000',
                                    'vcc': '3.4600',
                                    'tx_bias': '70.0000',
                                    'tx_power': '1.0000',
                                    'rx_power': '0.5012'
                                },
                                'warning_lower': {
                                    'temperature': '-35.0000',
                                    'vcc': '3.1300',
                                    'tx_bias': '4.0000',
                                    'tx_power': '0.3162',
                                    'rx_power': '0.0040'
                                }
                            }
                        },
                        'statistics': {
                            'H800S003984': {
                                'temperature': {
                                    'average': '43.1567',
                                    'count': 600,
                                    'variance': '8.0836',
                                    'minimum': '36.3164',
                                    'maximum': '46.7344'
                                },
                                'vcc': {
                                    'average': '3.1721',
                                    'count': 600,
                                    'variance': '0.0000',
                                    'minimum': '3.1559',
                                    'maximum': '3.1823'
                                },
                                'tx_bias': {
                                    'average': '18.7327',
                                    'count': 600,
                                    'variance': '0.0126',
                                    'minimum': '18.4620',
                                    'maximum': '18.8240'
                                },
                                'tx_power': {
                                    'average': '0.6180',
                                    'count': 600,
                                    'variance': '0.0000',
                                    'minimum': '0.6180',
                                    'maximum': '0.6180'
                                },
                                'rx_power': {
                                    'average': '0.0000',
                                    'count': 600,
                                    'variance': '0.0000',
                                    'minimum': '0.0000',
                                    'maximum': '0.0000'
                                }
                            }
                        }
                    }
                }
            })
        }

    def test_measurements(self):
        node = self.create_node()

        self.run_processor(
            sfp_processors.SFP,
            node=node,
            context=self.generate_context()
        )

        modules = list(node.monitoring.irnas.sfp())
        self.assertEqual(len(modules), 1)
        module = modules[0]
        self.assertEqual(module.serial_number, 'H800S003984')
        self.assertEqual(module.bus, '/dev/i2c-1')
        self.assertEqual(module.manufacturer, 'OEM')
        self.assertEqual(module.revision, '1.0')
        self.assertEqual(module.type, 3)
        self.assertEqual(module.connector, 7)
        self.assertEqual(module.bitrate, 1300)
        self.assertEqual(module.wavelength, 1310)

        self.assertEqual(module.temperature, 43.1567)
        self.assertEqual(module.temperature_variance, 8.0836)
        self.assertEqual(module.temperature_minimum, 36.3164)
        self.assertEqual(module.temperature_maximum, 46.7344)

        self.assertEqual(module.vcc, 3.1721)
        self.assertEqual(module.vcc_variance, 0.0)
        self.assertEqual(module.vcc_minimum, 3.1559)
        self.assertEqual(module.vcc_maximum, 3.1823)

        self.assertEqual(module.tx_bias, 18.7327)
        self.assertEqual(module.tx_bias_variance, 0.0126)
        self.assertEqual(module.tx_bias_minimum, 18.4620)
        self.assertEqual(module.tx_bias_maximum, 18.8240)

        self.assertEqual(module.tx_power, 0.6180)
        self.assertEqual(module.tx_power_variance, 0.0)
        self.assertEqual(module.tx_power_minimum, 0.6180)
        self.assertEqual(module.tx_power_maximum, 0.6180)

        self.assertEqual(module.rx_power, 0)
        self.assertEqual(module.rx_power_variance, 0.0)
        self.assertEqual(module.rx_power_minimum, 0.0)
        self.assertEqual(module.rx_power_maximum, 0.0)

        self.assertEqual(module.rx_power_dbm, -40)
        self.assertEqual(module.rx_power_dbm_variance, -40)
        self.assertEqual(module.rx_power_dbm_minimum, -40)
        self.assertEqual(module.rx_power_dbm_maximum, -40)

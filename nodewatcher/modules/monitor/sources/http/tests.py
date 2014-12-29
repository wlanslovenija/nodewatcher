import unittest

from . import parser


class TestContext(dict):
    pass


class HttpParserTestCase(unittest.TestCase):
    def test_parser_v2(self):
        p = parser.HttpTelemetryParser(data="""
;
; nodewatcher monitoring system
;
META.version: 2
META.modules.core-clients.serial: 1
dhcp.client0.ip: 10.254.134.69
dhcp.client1.ip: 10.254.134.92
iptables.redirection_problem: 0
net.losses: 0
META.modules.core-general.serial: 3
general.uuid: 78b610f8-b8a3-4768-bbed-2e779016c495
general.hostname: fri
general.version: git.f037240
general.local_time: 1401644593
general.uptime: 1200189.99 1135165.89
general.loadavg: 0.07 0.09 0.06 1/39 21192
general.memfree: 7876
general.buffers: 1788
""")
        tree = TestContext()
        p.parse_into(tree)

        self.assertIsInstance(tree, TestContext)
        self.assertIn('_meta', tree)
        self.assertIn('META', tree)
        self.assertIn('dhcp', tree)
        self.assertIn('net', tree)
        self.assertIn('general', tree)
        self.assertIsInstance(tree['META'], TestContext)
        self.assertIsInstance(tree['general'], TestContext)
        self.assertIsInstance(tree['_meta'], TestContext)

        self.assertEquals(tree['general']['memfree'], '7876')
        self.assertEquals(tree['general']['buffers'], '1788')
        self.assertEquals(tree['general']['loadavg'], '0.07 0.09 0.06 1/39 21192')
        self.assertEquals(tree['META']['version'], '2')

        self.assertEquals(tree['_meta']['version'], 2)

    def test_parser_v3(self):
        p = parser.HttpTelemetryParser(data='{ "core.general": { "uuid": "64840ad9-aac1-4494-b4d1-9de5d8cbedd9", "hostname": "lem-1", "version": "git.12f427d", "kernel": "3.10.36", "local_time": 1401644630, "uptime": 962, "hardware": { "board": "tl-wr741nd-v4", "model": "TP-Link TL-WR740N\/ND v4" }, "_meta": { "version": 4 } }, "core.interfaces": { "lo": { "name": "lo", "config": "loopback", "addresses": [ { "family": "ipv4", "address": "127.0.0.1", "mask": 8 } ], "mac": "00:00:00:00:00:00", "mtu": 65536, "up": true, "carrier": true, "statistics": { "collisions": 0, "rx_frame_errors": 0, "tx_compressed": 0, "multicast": 0, "rx_length_errors": 0, "tx_dropped": 0, "rx_bytes": 7736, "rx_missed_errors": 0, "tx_errors": 0, "rx_compressed": 0, "rx_over_errors": 0, "tx_fifo_errors": 0, "rx_crc_errors": 0, "rx_packets": 50, "tx_heartbeat_errors": 0, "rx_dropped": 0, "tx_aborted_errors": 0, "tx_packets": 50, "rx_errors": 0, "tx_bytes": 7736, "tx_window_errors": 0, "rx_fifo_errors": 0, "tx_carrier_errors": 0 } }, "wlan0": { "name": "wlan0", "config": "mesh", "addresses": [ { "family": "ipv4", "address": "10.254.147.225", "mask": 16 } ], "up": true, "carrier": true, "statistics": { "collisions": 0, "rx_frame_errors": 0, "tx_compressed": 0, "multicast": 0, "rx_length_errors": 0, "tx_dropped": 0, "rx_bytes": 0, "rx_missed_errors": 0, "tx_errors": 0, "rx_compressed": 0, "rx_over_errors": 0, "tx_fifo_errors": 0, "rx_crc_errors": 0, "rx_packets": 0, "tx_heartbeat_errors": 0, "rx_dropped": 0, "tx_aborted_errors": 0, "tx_packets": 4, "rx_errors": 0, "tx_bytes": 480, "tx_window_errors": 0, "rx_fifo_errors": 0, "tx_carrier_errors": 0 } }, "br-clients": { "name": "br-clients", "config": "clients", "addresses": [ { "family": "ipv4", "address": "10.254.147.225", "mask": 27 } ], "mac": "a0:f3:c1:a7:ec:f3", "mtu": 1500, "up": true, "carrier": true, "statistics": { "collisions": 0, "rx_frame_errors": 0, "tx_compressed": 0, "multicast": 0, "rx_length_errors": 0, "tx_dropped": 0, "rx_bytes": 0, "rx_missed_errors": 0, "tx_errors": 0, "rx_compressed": 0, "rx_over_errors": 0, "tx_fifo_errors": 0, "rx_crc_errors": 0, "rx_packets": 0, "tx_heartbeat_errors": 0, "rx_dropped": 0, "tx_aborted_errors": 0, "tx_packets": 564, "rx_errors": 0, "tx_bytes": 59008, "tx_window_errors": 0, "rx_fifo_errors": 0, "tx_carrier_errors": 0 } }, "eth0": { "name": "eth0", "config": "clients", "parent": "br-clients", "mac": "a0:f3:c1:a7:ec:f3", "mtu": 1500, "up": true, "carrier": false, "statistics": { "collisions": 0, "rx_frame_errors": 0, "tx_compressed": 0, "multicast": 0, "rx_length_errors": 0, "tx_dropped": 0, "rx_bytes": 0, "rx_missed_errors": 0, "tx_errors": 0, "rx_compressed": 0, "rx_over_errors": 0, "tx_fifo_errors": 0, "rx_crc_errors": 0, "rx_packets": 0, "tx_heartbeat_errors": 0, "rx_dropped": 0, "tx_aborted_errors": 0, "tx_packets": 0, "rx_errors": 0, "tx_bytes": 0, "tx_window_errors": 0, "rx_fifo_errors": 0, "tx_carrier_errors": 0 } }, "wlan0-1": { "name": "wlan0-1", "config": "clients", "parent": "br-clients", "up": true, "carrier": true, "statistics": { "collisions": 0, "rx_frame_errors": 0, "tx_compressed": 0, "multicast": 0, "rx_length_errors": 0, "tx_dropped": 0, "rx_bytes": 0, "rx_missed_errors": 0, "tx_errors": 0, "rx_compressed": 0, "rx_over_errors": 0, "tx_fifo_errors": 0, "rx_crc_errors": 0, "rx_packets": 0, "tx_heartbeat_errors": 0, "rx_dropped": 0, "tx_aborted_errors": 0, "tx_packets": 568, "rx_errors": 0, "tx_bytes": 69640, "tx_window_errors": 0, "rx_fifo_errors": 0, "tx_carrier_errors": 0 } }, "digger0": { "name": "digger0", "config": "digger0", "addresses": [ { "family": "ipv4", "address": "10.254.147.226", "mask": 16 } ], "mac": "b6:c1:50:66:c8:42", "mtu": 1488, "up": true, "carrier": true, "statistics": { "collisions": 0, "rx_frame_errors": 0, "tx_compressed": 0, "multicast": 0, "rx_length_errors": 0, "tx_dropped": 0, "rx_bytes": 3866556, "rx_missed_errors": 0, "tx_errors": 0, "rx_compressed": 0, "rx_over_errors": 0, "tx_fifo_errors": 0, "rx_crc_errors": 0, "rx_packets": 2952, "tx_heartbeat_errors": 0, "rx_dropped": 1, "tx_aborted_errors": 0, "tx_packets": 573, "rx_errors": 1, "tx_bytes": 63413, "tx_window_errors": 0, "rx_fifo_errors": 0, "tx_carrier_errors": 0 } }, "digger1": { "name": "digger1", "config": "digger1", "addresses": [ { "family": "ipv4", "address": "10.254.147.227", "mask": 16 } ], "mac": "2e:cd:57:19:51:b1", "mtu": 1488, "up": true, "carrier": true, "statistics": { "collisions": 0, "rx_frame_errors": 0, "tx_compressed": 0, "multicast": 0, "rx_length_errors": 0, "tx_dropped": 0, "rx_bytes": 3036420, "rx_missed_errors": 0, "tx_errors": 0, "rx_compressed": 0, "rx_over_errors": 0, "tx_fifo_errors": 0, "rx_crc_errors": 0, "rx_packets": 2212, "tx_heartbeat_errors": 0, "rx_dropped": 0, "tx_aborted_errors": 0, "tx_packets": 506, "rx_errors": 0, "tx_bytes": 57924, "tx_window_errors": 0, "rx_fifo_errors": 0, "tx_carrier_errors": 0 } }, "eth1": { "name": "eth1", "config": "wan", "addresses": [ { "family": "ipv4", "address": "192.168.34.108", "mask": 24 } ], "mac": "a0:f3:c1:a7:ec:f5", "mtu": 1500, "up": true, "carrier": true, "speed": "100F", "statistics": { "collisions": 0, "rx_frame_errors": 0, "tx_compressed": 0, "multicast": 0, "rx_length_errors": 0, "tx_dropped": 0, "rx_bytes": 7894764, "rx_missed_errors": 0, "tx_errors": 0, "rx_compressed": 0, "rx_over_errors": 0, "tx_fifo_errors": 0, "rx_crc_errors": 0, "rx_packets": 7653, "tx_heartbeat_errors": 0, "rx_dropped": 0, "tx_aborted_errors": 0, "tx_packets": 2837, "rx_errors": 0, "tx_bytes": 591759, "tx_window_errors": 0, "rx_fifo_errors": 0, "tx_carrier_errors": 0 } }, "_meta": { "version": 3 } }, "core.resources": { "load_average": { "avg1": "0.05", "avg5": "0.18", "avg15": "0.27" }, "memory": { "total": 28988, "free": 5888, "buffers": 2016, "cache": 6348 }, "connections": { "ipv4": { "tcp": 3, "udp": 15 }, "ipv6": { "tcp": 2, "udp": 1 } }, "processes": { "running": 3, "sleeping": 33, "blocked": 0, "zombie": 0, "stopped": 0, "paging": 0 }, "cpu": { "user": 2, "system": 0, "nice": 2, "idle": 96, "iowait": 0, "irq": 0, "softirq": 0 }, "_meta": { "version": 2 } }, "core.wireless": { "wlan0-1": { "phy": "phy0", "ssid": "open.wlan-si.net", "bssid": "A2:F3:C1:A7:EC:F4", "country": "SI", "mode": "Master", "channel": 8, "frequency": 2447, "txpower": 18, "noise": -95 }, "wlan0": { "phy": "phy0", "ssid": "mesh.wlan-si.net", "bssid": "02:CA:FF:EE:BA:BE", "country": "SI", "mode": "Ad-Hoc", "channel": 8, "frequency": 2447, "txpower": 18, "noise": -95 }, "_meta": { "version": 3 } } }')
        tree = TestContext()
        p.parse_into(tree)

        self.assertIsInstance(tree, TestContext)
        self.assertIn('core', tree)
        self.assertIn('_meta', tree)
        self.assertIn('general', tree['core'])
        self.assertIn('resources', tree['core'])
        self.assertIn('interfaces', tree['core'])
        self.assertIn('wireless', tree['core'])
        self.assertIsInstance(tree['core'], TestContext)
        self.assertIsInstance(tree['core']['general'], TestContext)
        self.assertIsInstance(tree['core']['resources'], TestContext)
        self.assertIsInstance(tree['_meta'], TestContext)

        self.assertEquals(tree['core']['general']['local_time'], 1401644630)
        self.assertEquals(tree['core']['general']['uuid'], '64840ad9-aac1-4494-b4d1-9de5d8cbedd9')

        self.assertEquals(tree['_meta']['version'], 3)

import datetime
import ijson
import traceback
import math
import time

from django.core.management import base

from django_datastream import datastream


class Command(base.BaseCommand):
    help = "Imports legacy nodewatcher v2 data into datastream."
    requires_model_validation = True

    def handle(self, *args, **options):
        if len(args) != 1:
            raise base.CommandError('Missing filename argument!')

        input_filename = args[0]
        try:
            input_file = open(input_filename, 'r')
        except IOError:
            raise base.CommandError("Unable to open file '%s'!" % input_filename)

        self.stdout.write("Starting import process...\n")
        start_time = time.time()
        item_index = 0
        data_points = 0
        ensured_streams = {}
        for item in ijson.items(input_file, 'items.item'):
            timestamp = datetime.datetime.utcfromtimestamp(item['s'])
            item_index += 1
            if item_index % 100 == 0:
                self.stdout.write("[%d/s]\n" % (data_points / (time.time() - start_time)))

            try:
                streams = self.import_data(item)
            except:
                self.stdout.write("=== ERROR: Exception ocurred while processing input stream!\n")
                self.stdout.write("--- Exception:\n")
                self.stdout.write(traceback.format_exc())
                self.stdout.write("\n")
                self.stdout.write("--- Item index:\n")
                self.stdout.write("%s\n" % item_index)
                self.stdout.write("--- Item data:\n")
                self.stdout.write(repr(item))
                self.stdout.write("\n\n")
                raise base.CommandError("Exception ocurred, terminating import.")

            for stream in streams:
                stream_key = tuple(sorted([x for x in stream['tags'].items() if type(x[1]) != dict]))
                if stream_key not in ensured_streams:
                    stream_id = datastream.ensure_stream(
                        stream['tags'],
                        stream['tags'],
                        stream.get('value_downsamplers', [
                            'mean',
                            'sum',
                            'min',
                            'max',
                            'sum_squares',
                            'std_dev',
                            'count'
                        ]),
                        datastream.Granularity.Minutes
                    )
                    ensured_streams[stream_key] = stream_id
                else:
                    stream_id = ensured_streams[stream_key]

                try:
                    datastream.append(stream_id, stream['value'], timestamp)
                    data_points += 1
                except:
                    # Skip datapoints on errors
                    self.stdout.write("=== WARNING: Skipping datapoint due to exception!\n")
                    self.stdout.write("--- Exception:\n")
                    self.stdout.write(traceback.format_exc())
                    self.stdout.write("\n")
                    self.stdout.write("--- Datapoint:\n")
                    self.stdout.write("%s\n" % item['s'])
                    self.stdout.write(repr(stream['value']))
                    self.stdout.write("\n\n")
                    continue

    def import_data(self, item):
        return {
            # NumProc
            -1: self.import_num_processes,
            # MemUsage
            0: self.import_memory_usage,
            # LoadAverage
            1: self.import_load_average,
            # RTT
            2: self.import_rtt,
            # LQ
            3: self.import_link_quality,
            # PacketLoss
            4: self.import_packet_loss,
            # Traffic
            10: self.import_traffic,
            # ETX
            11: self.import_etx,
            # Uptime
            1001: self.import_uptime,
        }.get(item['t'], lambda x: [])(item)

    def import_uptime(self, item):
        return [
            # Stream for uptime field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.status',
                    'name': 'uptime',
                },
                'value': float(item['d']['uptime']) if item['d'] is not None else None,
            },
        ]

    def import_load_average(self, item):
        return [
            # Stream for loadavg_1min field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'loadavg_1min',
                },
                'value': float(item['d']['la1min']) if item['d'] is not None else None,
            },
            # Stream for loadavg_5min field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'loadavg_5min',
                },
                'value': float(item['d']['la5min']) if item['d'] is not None else None,
            },
            # Stream for loadavg_15min field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'loadavg_15min',
                },
                'value': float(item['d']['la15min']) if item['d'] is not None else None,
            },
        ]

    def import_memory_usage(self, item):
        return [
            # Stream for memory_free field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'memory_free',
                },
                'value': int(item['d']['memfree']) if item['d'] is not None else None,
            },
            # Stream for memory_buffers field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'memory_buffers',
                },
                'value': int(item['d']['buffers']) if item['d'] is not None else None,
            },
            # Stream for memory_cache field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'memory_cache',
                },
                'value': int(item['d']['cached']) if item['d'] is not None else None,
            },
        ]

    def import_num_processes(self, item):
        return [
            # Stream for processes field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'processes',
                },
                'value': int(item['d']['nproc']) if item['d'] is not None else None,
            },
        ]

    def import_traffic(self, item):
        return [
            # Stream for tx_bytes field
            {
                'value_downsamplers': [],
                'tags': {
                    'node': item['n'],
                    'registry_id': 'core.interfaces',
                    'name': 'tx_bytes',
                    'interface': item['m'],
                    'visualization': {'hidden': True},
                },
                'value': int(item['d']['upload']) if item['d'] is not None else None,
            },
            # Stream for rx_bytes field
            {
                'value_downsamplers': [],
                'tags': {
                    'node': item['n'],
                    'registry_id': 'core.interfaces',
                    'name': 'rx_bytes',
                    'interface': item['m'],
                    'visualization': {'hidden': True},
                },
                'value': int(item['d']['download']) if item['d'] is not None else None,
            },
        ]

    def import_link_quality(self, item):
        return [
            # Stream for lq field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.routing.topology',
                    'name': 'lq' if item['m'] else 'average_lq',
                    'link': item['m'] or None,
                    'protocol': 'olsr',
                },
                'value': float(item['d']['lq']) if item['d'] is not None else None,
            },
            # Stream for ilq field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.routing.topology',
                    'name': 'ilq' if item['m'] else 'average_ilq',
                    'link': item['m'] or None,
                    'protocol': 'olsr',
                },
                'value': float(item['d']['ilq']) if item['d'] is not None else None,
            },
        ]

    def import_etx(self, item):
        return [
            # Stream for etx field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.routing.topology',
                    'name': 'etx' if item['m'] else 'average_etx',
                    'link': item['m'] or None,
                    'protocol': 'olsr',
                },
                'value': float(item['d']['etx']) if item['d'] is not None else None,
            },
        ]

    def import_rtt(self, item):
        m = float(item['d']['rtt']) if item['d'] is not None else None
        l = float(item['d']['rtt_min']) if item['d'] is not None else None
        u = float(item['d']['rtt_max']) if item['d'] is not None else None

        points = [point for point in [l, m, u] if point is not None]
        s = sum(points)
        ss = sum([x ** 2 for x in points])
        try:
            d = math.sqrt((3 * ss - s ** 2) / (3.0 * (3 - 1)))
        except ValueError:
            d = 0

        return [
            # Stream for rtt_minimum field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.measurement.rtt',
                    'name': 'rtt',
                    'packet_size': 56,
                },
                'value': {
                    'm': m, # mean
                    'l': l, # minimum
                    'u': u, # maximum
                    'c': 3, # count
                    'd': d, # std. dev
                    's': s, # sum
                    'q': ss, # sum of squares
                },
            },
        ]

    def import_packet_loss(self, item):
        return [
            # Stream for packet_loss field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.measurement.rtt',
                    'name': 'packet_loss',
                    'packet_size': 56,
                },
                'value': float(item['d']['loss_def']) if (item['d'] or {}).get('loss_def', None) is not None else None,
            },
            # Stream for packet_loss field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.measurement.rtt',
                    'name': 'packet_loss',
                    'packet_size': 100,
                },
                'value': float(item['d']['loss_100']) if (item['d'] or {}).get('loss_100', None) is not None else None,
            },
            # Stream for packet_loss field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.measurement.rtt',
                    'name': 'packet_loss',
                    'packet_size': 500,
                },
                'value': float(item['d']['loss_500']) if (item['d'] or {}).get('loss_500', None) is not None else None,
            },
            # Stream for packet_loss field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.measurement.rtt',
                    'name': 'packet_loss',
                    'packet_size': 1000,
                },
                'value': float(item['d']['loss_1000']) if (item['d'] or {}).get('loss_1000', None) is not None else None,
            },
            # Stream for packet_loss field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.measurement.rtt',
                    'name': 'packet_loss',
                    'packet_size': 1480,
                },
                'value': float(item['d']['loss_1480']) if (item['d'] or {}).get('loss_1480', None) is not None else None,
            },
        ]

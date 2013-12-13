import datetime
import ijson
import traceback

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
        for item in ijson.items(input_file, 'items.item'):
            timestamp = datetime.datetime.utcfromtimestamp(item['s'])
            streams = self.import_data(item)

            for stream in streams:
                stream_id = datastream.ensure_stream(
                    stream['tags'],
                    stream['tags'],
                    [
                        'mean',
                        'sum',
                        'min',
                        'max',
                        'sum_squares',
                        'std_dev',
                        'count'
                    ],
                    datastream.Granularity.Minutes
                )

                try:
                    datastream.append(stream_id, stream['value'], timestamp)
                except:
                    # Skip datapoints on errors
                    sys.stdout.write("WARNING: Skipping datapoint due to exception!\n")
                    sys.stdout.write(traceback.format_exc())
                    sys.stdout.write("\n")
                    continue

    def import_data(self, item):
        return {
            # NumProc
            -1: self.import_num_processes,
            # MemUsage
            0: self.import_memory_usage,
            # LoadAverage
            1: self.import_load_average,
            # LQ
            3: self.import_link_quality,
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
                'value': float(item['d']['uptime']),
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
                'value': float(item['d']['la1min']),
            },
            # Stream for loadavg_5min field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'loadavg_5min',
                },
                'value': float(item['d']['la5min']),
            },
            # Stream for loadavg_15min field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'loadavg_15min',
                },
                'value': float(item['d']['la15min']),
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
                'value': int(item['d']['memfree']),
            },
            # Stream for memory_buffers field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'memory_buffers',
                },
                'value': int(item['d']['buffers']),
            },
            # Stream for memory_cache field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'system.resources.general',
                    'name': 'memory_cache',
                },
                'value': int(item['d']['cached']),
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
                'value': int(item['d']['nproc']),
            },
        ]

    def import_traffic(self, item):
        return [
            # Stream for tx_bytes field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'core.interfaces',
                    'name': 'tx_bytes',
                    'interface': item['m'],
                },
                'value': int(item['d']['upload']),
            },
            # Stream for rx_bytes field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'core.interfaces',
                    'name': 'rx_bytes',
                    'interface': item['m'],
                },
                'value': int(item['d']['download']),
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
                },
                'value': float(item['d']['lq']),
            },
            # Stream for ilq field
            {
                'tags': {
                    'node': item['n'],
                    'registry_id': 'network.routing.topology',
                    'name': 'ilq' if item['m'] else 'average_ilq',
                    'link': item['m'] or None,
                },
                'value': float(item['d']['ilq']),
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
                },
                'value': float(item['d']['etx']),
            },
        ]

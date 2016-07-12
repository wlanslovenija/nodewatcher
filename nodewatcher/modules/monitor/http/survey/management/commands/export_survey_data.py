import io
import json
import time
import datetime

from django.core.management import base

from django_datastream import datastream


class Command(base.BaseCommand):
    help = "Consolidates survey data from all nodes and exports the meta graph as a JSON file."

    def add_arguments(self, parser):

        # Optional arguments
        parser.add_argument(
            '--timestamp',
            type=int,
            action='store',
            dest='timestamp',
            help="All the data will be collected between this UNIX timestamp and two hours preceding it."
        )

        parser.add_argument(
            '-f',
            '--filename',
            type=str,
            action='store',
            dest='filename',
            default='survey_export',
            help="Optional filename",
        )

        parser.add_argument(
            '--include-timestamp-in-filename',
            type=bool,
            action='store',
            dest='store_timestamp',
            default=False,
            help="Include timestamp in filename?",
        )

    def handle(self, *args, **options):
        """
        Exports the latest survey data graph as a JSON file into the root directory.
        """

        timestamp = options['timestamp']
        if timestamp:
            latest_survey_datetime = datetime.datetime.fromtimestamp(timestamp)
        else:
            latest_survey_datetime = datetime.datetime.utcnow()

        filename = options['filename']

        streams = datastream.find_streams({'module': 'monitor.http.survey'})

        # Create a meta graph
        meta_vertices, meta_edges = [], []
        friendly_nodes = []
        for stream in streams:
            datapoint_iterator = datastream.get_data(
                stream_id=stream['stream_id'],
                granularity=stream['highest_granularity'],
                start=(latest_survey_datetime - datetime.timedelta(hours=2)),
                reverse=True,
            )
            try:
                stream_graph = datapoint_iterator[0]['v']
                for vertex in stream_graph['v']:
                    meta_vertices.append(vertex)
                    if 'bssids' in vertex:
                        friendly_nodes.append(vertex)
                for edge in stream_graph['e']:
                    meta_edges.append(edge)
            except IndexError:
                pass

        if not meta_vertices or not meta_edges:
            self.stdout.write(self.style.ERROR("Insufficient survey data in the datastream during this time period."))
            return

        meta_graph = {
            'v': meta_vertices,
            'e': meta_edges,
        }

        exported_graph = {
            'graph': meta_graph,
            'friendly_nodes': friendly_nodes,
        }

        if options['store_timestamp']:
            filename = '{0}{1}.json'.format(filename, timestamp)
        else:
            filename = '{0}.json'.format(filename)

        with io.open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(exported_graph, ensure_ascii=False))

        self.stdout.write(self.style.SUCCESS("Successfully exported survey data."))

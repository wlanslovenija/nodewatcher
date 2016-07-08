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
            default=int(time.time()),
            help="Number of surveys to export"
        )

        parser.add_argument(
            '--label',
            type=str,
            action='store',
            dest='label',
            default='survey_export',
            help="Optional label for the filename",
        )

    def handle(self, *args, **options):
        """
        Exports the latest survey data graph as a JSON file into the root directory.
        """

        timestamp = options['timestamp']
        date_from_timestamp = datetime.datetime.fromtimestamp(timestamp)
        label = options['label']

        streams = datastream.find_streams({'module': 'monitor.http.survey'})

        # Create a meta graph
        meta_vertices, meta_edges = [], []
        friendly_nodes = []
        for stream in streams:
            datapoint_iterator = datastream.get_data(
                stream_id=stream['stream_id'],
                granularity=stream['highest_granularity'],
                start=stream['latest_datapoint'],
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
        meta_graph = {
            'v': meta_vertices,
            'e': meta_edges,
        }

        exported_graph = {
            'graph': meta_graph,
            'friendly_nodes': friendly_nodes,
        }

        timestamp = int(time.time())

        if label:
            filename = label + str(timestamp) + '.json'
        else:
            filename = 'survey_export' + str(timestamp) + '.json'

        with io.open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(exported_graph, ensure_ascii=False))

        self.stdout.write(self.style.SUCCESS("Successfully exported survey data."))

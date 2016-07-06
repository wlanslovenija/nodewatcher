from django.core.management import base

from django_datastream import datastream

import json

import io

class Command(base.BaseCommand):
    help = 'Consolidates survey data from all nodes and exports the meta graph as a JSON file.'

    def add_arguments(self, parser):

        # Optional arguments
        parser.add_argument(
            '--surveys-to-export',
            type=int,
            action='store',
            dest='number',
            default=1,
            help='Number of surveys to export'
        )

        parser.add_argument(
            '--label',
            type=str,
            action='store',
            dest='label',
            help='Optional label for the filename',
        )

    def handle(self, *args, **options):

        streams = datastream.find_streams({'module': 'monitor.http.survey'})
        print("len of streams is ")
        print(len(streams))

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
        print(meta_graph)
        with io.open('data.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(meta_graph, ensure_ascii=False))
        number = options['number']
        if number:
            print(number)
            self.stdout.write(self.style.SUCCESS(number))
        label = options['label']
        if label:
            self.stdout.write(self.style.SUCCESS(label))

        self.stdout.write(self.style.SUCCESS("Successfully called export survey data"))

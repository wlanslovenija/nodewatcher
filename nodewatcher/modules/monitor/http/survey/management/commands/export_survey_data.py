import io
import json
import datetime

from django.core.management import base

from django_datastream import datastream


class Command(base.BaseCommand):
    help = """
    Consolidates the latest survey data within the specified time interval
    from all nodes and exports the meta graph as a JSON file.
    """

    def add_arguments(self, parser):
        # Optional arguments
        parser.add_argument(
            '--datetime',
            type=str,
            action='store',
            dest='datetime',
            help="""
            All the data will be collected between this UTC date
            (format 'yyyy-mm-ddThh:mm:ss' (i.e. '2007-04-10T12:00:00')
            and two hours preceding it.
            """,
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

    def handle(self, *args, **options):
        """
        Exports the latest survey data graph as a JSON file into the root directory.
        """

        parsed_datetime = None
        input_datetime = options['datetime']
        filename = options['filename']

        if input_datetime:
            try:
                parsed_datetime = datetime.datetime.strptime(options['datetime'], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                self.stdout.write(self.style.ERROR("Unable to parse datetime."))
                return

        exported_graph = extract_survey_graph(parsed_datetime)

        if not exported_graph:
            raise base.CommandError("Insufficient survey data in the datastream during this time period.")

        filename = '{0}.json'.format(filename)

        with io.open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(exported_graph, ensure_ascii=False))

        self.stdout.write(self.style.SUCCESS("Successfully exported survey data."))


def extract_survey_graph(parsed_datetime=None):
    """
    Extracts a graph of the survey during a specified time period. Only the latest data
    from specified datetime and two hours preceding the datetime will be used.

    :param parsed_datetime: Datetime object according to the UTC timezone.
    :return: A dictionary that contains the graph under the 'graph' key.
    """

    if parsed_datetime:
        latest_survey_datetime = parsed_datetime
    else:
        latest_survey_datetime = datetime.datetime.utcnow()

    streams = datastream.find_streams({'module': 'monitor.http.survey'})

    # Create a meta graph
    meta_vertices, meta_edges = [], []
    friendly_nodes = []
    latest_data_timepoint = 0

    for stream in streams:
        datapoint_iterator = datastream.get_data(
            stream_id=stream['stream_id'],
            granularity=stream['highest_granularity'],
            start=(latest_survey_datetime - datetime.timedelta(hours=2)),
            end=latest_survey_datetime,
            reverse=True,
        )
        try:
            stream_graph = datapoint_iterator[0]['v']
            for vertex in stream_graph['v']:
                meta_vertices.append(vertex)
                if 'b' in vertex:
                    friendly_nodes.append(vertex['i'])
                    for bssid in vertex['b']:
                        friendly_nodes.append(bssid)
            for edge in stream_graph['e']:
                meta_edges.append(edge)
            if not latest_data_timepoint or datapoint_iterator[0]['t'] > latest_data_timepoint:
                latest_data_timepoint = datapoint_iterator[0]['t']
        except IndexError:
            pass

    if not meta_vertices or not meta_edges:
        return

    meta_graph = {
        'v': meta_vertices,
        'e': meta_edges,
    }

    exported_graph = {
        'graph': meta_graph,
        'friendly_nodes': friendly_nodes,
        'timepoint': str(latest_data_timepoint)
    }

    return exported_graph

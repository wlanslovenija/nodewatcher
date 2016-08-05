import datetime

from django.core.management import base

from django_datastream import datastream


def all_nodes_survey_graph(at):
    """
    Returns a graph of the site survey data for a specified time. Only the latest datapoint for
    each node between the specified time and two hours preceding the time will be used.

    :param at: A datetime object.
    :return: A dictionary that contains the graph under the "graph" key.
    """

    streams = datastream.find_streams({'module': 'monitor.http.survey'})

    vertices = []
    edges = []
    # List of BSSIDs of known nodes.
    known_nodes = []
    latest_datapoint_time = None

    for stream in streams:
        datapoints = datastream.get_data(
            stream_id=stream['stream_id'],
            granularity=stream['highest_granularity'],
            start=(at - datetime.timedelta(hours=2)),
            end=at,
            reverse=True,
        )
        try:
            stream_graph = datapoints[0]['v']
            for vertex in stream_graph['v']:
                vertices.append(vertex)
                if 'b' in vertex:
                    known_nodes.append(vertex['i'])
                    for bssid in vertex['b']:
                        known_nodes.append(bssid)
            for edge in stream_graph['e']:
                edges.append(edge)
            if not latest_datapoint_time or datapoints[0]['t'] > latest_datapoint_time:
                latest_datapoint_time = datapoints[0]['t']
        except IndexError:
            pass

    if not vertices or not edges:
        raise base.CommandError("Insufficient survey data in the datastream for the specified time.")

    exported_graph = {
        'graph': {
            'v': vertices,
            'e': edges,
        },
        'known_nodes': known_nodes,
        'timestamp': latest_datapoint_time
    }

    return exported_graph

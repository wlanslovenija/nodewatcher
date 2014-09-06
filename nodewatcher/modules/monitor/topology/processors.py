from django.utils.translation import gettext_noop

from django_datastream import datastream

from nodewatcher.core.monitor import processors as monitor_processors, models as monitor_models
from nodewatcher.modules.monitor.datastream import base as ds_base, fields as ds_fields
from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool


class TopologyStreams(ds_base.StreamsBase):
    topology = ds_fields.GraphField(tags={
        'title': gettext_noop("Network topology"),
        'description': gettext_noop("Network topology."),
        'visualization': {
            'type': 'graph',
        }
    })

    def get_stream_query_tags(self):
        return {'module': 'topology'}

    def get_stream_tags(self):
        return {'module': 'topology'}

    def get_stream_highest_granularity(self):
        return datastream.Granularity.Minutes


class TopologyStreamsData(object):
    def __init__(self, vertices, edges):
        self.topology = {
            'v': [{'i': uuid} for uuid in vertices],
            'e': edges,
        }

ds_pool.register(TopologyStreamsData, TopologyStreams)


class Topology(monitor_processors.NetworkProcessor):
    """
    Processor that stores the current overall network topology as a graph
    into datastream.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        vertices = set()
        edges = []
        for link in monitor_models.TopologyLink.objects.select_related('monitor').all():
            source_id = str(link.monitor.root_id)
            destination_id = str(link.peer_id)

            # Add vertex UUIDs
            vertices.add(source_id)
            vertices.add(destination_id)
            # Add edges
            edge = {'f': source_id, 't': destination_id}
            # Add any extra link attributes
            if hasattr(link, 'get_link_attributes'):
                edge.update(link.get_link_attributes())

            edges.append(edge)

        # Prepare graph for datastream processor
        context.datastream.topology = TopologyStreamsData(vertices, edges)

        return context, nodes

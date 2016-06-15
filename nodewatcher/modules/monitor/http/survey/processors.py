import datetime
import pytz

from django.utils.translation import gettext_noop

from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors
from nodewatcher.utils import ipaddr
from nodewatcher.modules.monitor.sources.http import processors as http_processors

from django_datastream import datastream

DATASTREAM_SUPPORTED = False
try:
    from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models, base as ds_base
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

    class SurveyInfoStreams(ds_base.StreamsBase):
        neighbor_graph = ds_fields.GraphField(tags={
            'title': gettext_noop("Neighbor topology"),
            'description': gettext_noop("Neighbor topology."),
            'visualization': {
                'type': 'graph',
                'initial_set': True,
            }
        })

        def get_module_name(self):
            return 'monitor.http.survey'

        def get_stream_query_tags(self):
            return {'module': 'survey'}

        def get_stream_tags(self):
            return {'module': 'survey'}

        def get_stream_highest_granularity(self):
            return datastream.Granularity.Minutes

    class SurveyInfoStreamsData(object):
        def __init__(self, vertices, edges):
            self.neighbor_graph = {
                'v': vertices,
                'e': edges
            }

    ds_pool.register(SurveyInfoStreamsData, SurveyInfoStreams)

    DATASTREAM_SUPPORTED = True
except ImportError:
    pass


class SurveyInfo(monitor_processors.NodeProcessor):
    """
    Stores neighbor's reported channel, BSSID and signal strength into the monitoring schema. A star shaped graph
    is constructed. Will only run if HTTP monitor module has previously fetched data.
    """

    @monitor_processors.depends_on_context("http", http_processors.HTTPTelemetryContext)
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        version = context.http.get_module_version('core.wireless')
        if version == 0:
            # Unsupported version or data fetch failed
            return context
        edges, vertices = [], []
        try:
            vertices.append(dict(i=str(node)))
            for radio in context.http.core.wireless.radios:
                for neighbor in context.http.core.wireless.radios[str(radio)]['survey']:
                    # add an edge for that neighbor
                    edge = {'f': str(node), 't': neighbor['bssid']}
                    vertices.append(dict(i=neighbor['bssid']))
                    edge['channel'] = neighbor['channel']
                    edge['signal'] = neighbor['signal']
                    edges.append(edge)
        except KeyError:
            pass
        except NameError:
            self.logger.warning("Error parsing JSON file for " + str(node))
        if DATASTREAM_SUPPORTED:
            # Store survey graph into datastream.
            context.datastream.survey_topology = SurveyInfoStreamsData(vertices, edges)

        return context

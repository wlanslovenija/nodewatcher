from django.utils.translation import gettext_noop

from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.modules.monitor.sources.http import processors as http_processors

from django_datastream import datastream

DATASTREAM_SUPPORTED = False
try:
    from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

    class SurveyInfoStreams(ds_models.RegistryRootStreams):
        neighbor_graph = ds_fields.GraphField(tags={
            'title': gettext_noop("Neighbor topology"),
            'description': gettext_noop("Neighbor topology."),
        })

        def get_module_name(self):
            return 'monitor.http.survey'

    class SurveyInfoStreamsData(object):
        def __init__(self, node, vertices, edges):
            self.node = node
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
            context.datastream.survey_topology = SurveyInfoStreamsData(node, vertices, edges)

        return context

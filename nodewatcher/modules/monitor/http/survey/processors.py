from django.utils.translation import gettext_noop as _

from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.modules.monitor.sources.http import processors as http_processors
from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool


class SurveyInfoStreams(ds_models.RegistryRootStreams):
    neighbor_graph = ds_fields.GraphField(tags={
        'title': _("Neighbor topology"),
        'description': _("Neighbor topology."),
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
            vertex_bssids = []
            for interface in context.http.core.wireless.interfaces.values():
                vertex_bssids.append(interface['bssid'])
            vertex = dict(i=str(node.uuid), bssids=vertex_bssids)
            vertices.append(vertex)
            for radio in context.http.core.wireless.radios.values():
                for neighbor in radio.survey:
                    vertices.append(dict(i=neighbor['bssid']))
                    # Add an edge for that neighbor
                    edge = {'f': str(node.uuid), 't': neighbor['bssid']}
                    edge['channel'] = neighbor['channel']
                    edge['signal'] = neighbor['signal']
                    edge['ssid'] = neighbor['ssid']
                    edges.append(edge)
        except KeyError:
            pass
        except NameError:
            self.logger.warning("Error parsing JSON file for " + str(node))
        # Store survey graph into datastream.
        context.datastream.survey_topology = SurveyInfoStreamsData(node, vertices, edges)
        return context

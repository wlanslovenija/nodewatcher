from django.utils.translation import gettext_noop as _

from django_datastream import datastream

from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.modules.monitor.sources.http import processors as http_processors
from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool


class SurveyInfoStreams(ds_models.RegistryRootStreams):
    neighbor_graph = ds_fields.GraphField(tags={
        'title': _("Neighborhood topology"),
        'description': _("Neighborhood topology."),
    })

    def get_module_name(self):
        return 'monitor.http.survey'

    def get_stream_highest_granularity(self):
        # The nodewatcher-agent performs a survey once every ~240 monitoring intervals according to
        # https://github.com/wlanslovenija/nodewatcher-agent/blob/master/modules/wireless.c#L362
        # and a monitoring run is performed every 30 seconds according to
        # https://github.com/wlanslovenija/nodewatcher-agent/blob/73f2b25db2c34ae7d70904bac31379a2243bade0/modules/wireless.c#L437
        # (master branch at https://github.com/wlanslovenija/nodewatcher-agent/blob/master/modules/wireless.c#L437).
        # So a survey is performed once every two hours, meaning that we use hourly granularity.
        return datastream.Granularity.Hours


class SurveyInfoStreamsData(object):
    def __init__(self, node, neighbor_graph):
        self.node = node
        self.neighbor_graph = neighbor_graph


ds_pool.register(SurveyInfoStreamsData, SurveyInfoStreams)


class SurveyInfo(monitor_processors.NodeProcessor):
    """
    Accesses the data collected during a WiFi survey of neighboring wireless access points / routers. Stores channel,
    BSSID, SSID and signal strength for each neighbor into the datastream. A star shaped graph is constructed. The
    source vertex contains an array of all BSSIDs of that node. Source vertex is stored according to its UUID,
    wherease all neighbors are stored according to their BSSIDs. Will only run if HTTP monitor module has previously
    fetched data.
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
            source_vertex_bssids = [interface.bssid for interface in context.http.core.wireless.interfaces.values()]
            source_vertex = {
                'i': str(node.uuid),
                'bssids': source_vertex_bssids,
            }
            vertices.append(source_vertex)
            for radio in context.http.core.wireless.radios.values():
                for neighbor in radio.survey:
                    vertices.append({'i': neighbor['bssid']})
                    # Add an edge for that neighbor.
                    edge = {'f': str(node.uuid), 't': neighbor['bssid']}
                    for field in ('channel', 'signal', 'ssid'):
                        if field in neighbor:
                            edge[field] = neighbor[field]
                    edges.append(edge)
        except KeyError:
            pass
        except NameError:
            self.logger.warning("Could not parse survey data for node: " + str(node))

        latest_stored_graph = None
        # Retrieve the latest stored datapoint, if it exists
        streams = datastream.find_streams({'node': node.uuid})
        if streams:
            latest_stream = streams[len(streams) - 1]
            datapoint_iterator = datastream.get_data(
                stream_id=latest_stream['stream_id'],
                granularity=latest_stream['highest_granularity'],
                start=latest_stream['latest_datapoint'])
            try:
                latest_stored_graph = datapoint_iterator[0]['v']
            except IndexError:
                pass

        latest_graph = {
            'v': vertices,
            'e': edges
        }

        if latest_graph != latest_stored_graph:
            # Store the latest graph into datastream.
            context.datastream.survey_topology = SurveyInfoStreamsData(node, latest_graph)
        return context

import datetime
import pytz

from django.utils.translation import gettext_noop

from nodewatcher.core.monitor import models as monitor_models, processors as monitor_processors
from nodewatcher.utils import ipaddr
from nodewatcher.modules.monitor.sources.http import processors as http_processors

DATASTREAM_SUPPORTED = False
try:
    from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
    from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

    class SurveyInfoStreams(ds_models.RegistryRootStreams):

        neighbor_graph = ds_fields.GraphField(tags={
            'title': gettext_noop("Neighbor topology"),
            'description': gettext_noop("Neigbhbor topology."),
            'visualization': {
                'type': 'graph',
                'initial_set': True,
            }
        })

        def get_module_name(self):
            return 'monitor.http.survey'

    class SurveyInfoStreamsData(object):
        def __init__(self, node, neighbor_graph):
            self.node = node
            self.neighbor_graph = neighbor_graph

    ds_pool.register(SurveyInfoStreamsData, SurveyInfoStreams)

    DATASTREAM_SUPPORTED = True
except ImportError:
    pass


class SurveyInfo(monitor_processors.NodeProcessor):
    """
    Stores node's reported channel, SNR and neighbor data into the monitoring schema. Will
    only run if HTTP monitor module has previously fetched data.
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
            # Unsupported version or data fetch failed (v0)
            return context

        try:
            for radio in context.http.core.wireless.radios:
                edge = {}
                for neighbor in context.http.core.wireless.radios[str(radio)]['survey']:
                    # add an edge for that neighbor
                    print(neighbor)
                    print(type(neighbor))
                    print(neighbor.keys())
                    print(neighbor)
                    #edge['channel'] = neighbor.channel
        except KeyError:
            pass
        except NameError:
            self.logger.warning("Error parsing JSON file for " + str(node))

        #channel = self.get_node_channel(context, node)
        #snr = self.get_node_snr(context, node)
        neighbors = self.get_node_neighbors(context, node)
        if DATASTREAM_SUPPORTED:
            # Store client count into datastream.
            context.datastream.monitor_http_clients = SurveyInfoStreamsData(node, '2', channel, snr, neighbors)

        return context

    def get_node_channel(self, context, node, frequency_band='2'):
        """
        Extracts the channel number from the context for the specified frequency band.

        :param context: Current context
        :param node: Node that is being processed
        :param frequency_band: either '2' or '5', corresponding to 2.4GHz and 5GHz.
        :return: channel currently assigned to the node at the specified frequency band.
        """

        try:
            for interface in context.http.core.wireless.interfaces:
                if str(context.http.core.wireless.interfaces[interface].frequency)[:1] == frequency_band:
                    return context.http.core.wireless.interfaces[interface].channel
        except NameError:
            self.logger.warning("Error parsing JSON file for " + str(node))

    def get_node_snr(self, context, node, frequency_band='2'):
        """
        Extracts the SNR from the context for the specified frequency band.

        :param context: Current context
        :param node: Node that is being processed
        :param frequency_band: either '2' or '5', corresponding to 2.4GHz and 5GHz.
        :return: SNR of the node at the specified frequency band.
        """
        edges = {}
        vertices = {}
        try:
            for interface in context.http.core.wireless.interfaces:
                # create an edge for every interface
                edge = {}
                edge = {'f': str(node), 't': destination_id}
                signal = 0
                noise = 0
                #try:
                #    signal = context.http.core.wireless.interfaces[interface].signal
                #    noise = context.http.core.wireless.interfaces[interface].noise
                #except KeyError:
                #    self.logger.warning("No SNR available for " + str(node))
                #    pass
                #edge['snr'] = signal - noise
                #edge['channel'] = context.http.core.wireless.interfaces[interface].channel

        except NameError:
            self.logger.warning("Error parsing JSON file for " + str(node))
        except KeyError:
            self.logger.warning("No SNR available for " + str(node))
            return 0

    def get_node_neighbors(self, context, node, frequency_band='2'):
        """
        Returns a dictionary of all access points in the vicinity along with the signal strength of each access point.

        :param context: Current context
        :param node: Node that is being processed
        :param: frequency_band: either '2' or '5', corresponding to 2.4GHz and 5GHz.
        :return: a dictionary of neighbors at the specified frequency band
        """

        if frequency_band == '2':
            frequency_band_max_channel = 14
            frequency_band_min_channel = 1
        elif frequency_band == '5':
            frequency_band_max_channel = 165
            frequency_band_min_channel = 36
        else:
            self.logger.warning("Frequency band not recognized")
            return

        try:
            for radio in context.http.core.wireless.radios:
                edge = {}
                for neighbor in context.http.core.wireless.radios[str(radio)]['survey']:
                    #add an edge for that neighbor
                    print(neighbor)
                    print(neighbor.keys())
                    edge['channel']= neighbor.channel
        except KeyError:
            pass
        except NameError:
            self.logger.warning("Error parsing JSON file for " + str(node))

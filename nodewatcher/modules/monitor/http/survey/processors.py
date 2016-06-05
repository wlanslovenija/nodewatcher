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
        snr = ds_fields.IntegerField(tags={
            'title': gettext_noop("SNR"),
            'description': gettext_noop("Node SNR."),
            'visualization': {
                'type': 'line',
                'initial_set': True,
                'time_downsamplers': ['mean'],
                'value_downsamplers': ['min', 'mean', 'max'],
                'minimum': 0.0,
            },
        })
        neighbor_count = ds_fields.IntegerField(tags={
            'title': gettext_noop("Neighbor count"),
            'description': gettext_noop("Number of detected access points."),
            'visualization': {
                'type': 'line',
                'initial_set': True,
                'time_downsamplers': ['mean'],
                'value_downsamplers': ['min', 'mean', 'max'],
                'minimum': 0.0,
            },
        })

        def get_module_name(self):
            return 'monitor.http.survey'

    class SurveyInfoStreamsData(object):
        def __init__(self, node, frequency, channel, snr, neighbors):
            self.node = node
            self.frequency = frequency  # either 2 or 5, corresponding to 2.4GHz and 5GHz
            self.channel = channel
            self.snr = snr
            self.neighbors = neighbors
            self.neighbor_count = len(self.neighbors)

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
        # Should I go through the existing clients as well?
        # existing_clients = {}
        #for client in node.monitoring.network.clients():
        #    existing_clients[client.client_id] = client

        version = context.http.get_module_version("core.wireless")
        if version == 0:
            # Unsupported version or data fetch failed (v0)
            return context

        channel = self.getNodeChannel(context, node)
        snr = self.getNodeSNR(context, node)
        neighbors = self.getNodeNeighbors(context, node)
        if DATASTREAM_SUPPORTED:
            # Store client count into datastream.
            context.datastream.monitor_http_clients = SurveyInfoStreamsData(node, "2", channel, snr, neighbors)

        return context

    def getNodeChannel(self, context, node, frequency_band="2"):
        """
        Extracts the channel number from the context for the specified frequency band.
        :param context: Current context
        :param node: Node that is being processed
        :param frequency_band: either "2" or "5", corresponding to 2.4GHz and 5GHz.
        :return: channel currently assigned to the node at the specified frequency band.
        """
        try:
            for interface in context.http.core.wireless.interfaces:
                if str(context.http.core.wireless.interfaces[interface].frequency)[:1] == frequency_band:
                    return context.http.core.wireless.interfaces[interface].channel
        except NameError:
            print("Error parsing JSON file for " + node)

    def getNodeSNR(self, context, node, frequency_band="2"):
        """
        Extracts the SNR from the context for the specified frequency band.
        :param context: Current context
        :param node: Node that is being processed
        :param frequency_band: either "2" or "5", corresponding to 2.4GHz and 5GHz.
        :return: SNR of the node at the specified frequency band.
        """
        try:
            for interface in context.http.core.wireless.interfaces:
                if str(context.http.core.wireless.interfaces[interface].frequency)[:1] == frequency_band:
                    signal = context.http.core.wireless.interfaces[interface].signal
                    noise = context.http.core.wireless.interfaces[interface].noise
                    if (not signal or not noise):
                        print("No SNR available for " + node)
                        return 0
                    else:
                        return signal - noise
        except NameError:
            print("Error parsing JSON file for " + node)
        except KeyError:
            print("No SNR available for " + node)
            return 0

    def getNodeNeighbors(self, context, node, frequency_band="2"):
        """
        returns a dictionary of all access points in the vicinity along with the signal strength of each access point.
        :param: frequency_band: either "2" or "5", corresponding to 2.4GHz and 5GHz.
        :return: a dictionary of neighbors at the specified frequency band
        """
        if frequency_band == "2":
            frequency_band_max_channel = 14
            frequency_band_min_channel = 1
        elif frequency_band == "5":
            frequency_band_max_channel = 165
            frequency_band_min_channel = 36
        else:
            print("Frequency band not recognized")
            return

        try:
            for radio in context.http.core.wireless.radios:
                for neighbor in context.http.core.wireless.radios[str(radio)]["survey"]:
                    if neighbor["channel"] <= frequency_band_max_channel and neighbor["channel"] >= frequency_band_min_channel:
                        return context.http.core.wireless.radios[radio]["survey"]
        except KeyError:
            pass
        except NameError:
            print("Error parsing JSON file for " + node)

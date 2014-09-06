import uuid

from django.db import models
from django.utils.translation import ugettext as _, gettext_noop

from nodewatcher.core.monitor import models as monitor_models
from nodewatcher.core.registry import registration
from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

# Randomly generated UUID for generating UUIDs for unknown nodes in the network from IPs
OLSR_UUID_NAMESPACE = uuid.UUID('f3f785f9-9580-4945-a43a-3e16f93783a6')
OLSR_PROTOCOL_NAME = 'olsr'

# Register the routing protocol option so interfaces can use it
registration.point('node.config').register_choice('core.interfaces#routing_protocol', registration.Choice(OLSR_PROTOCOL_NAME, _("OLSR")))

# Register the subnet announce option so interfaces can use it
registration.point('node.config').register_choice('core.interfaces.network#routing_announce', registration.Choice(OLSR_PROTOCOL_NAME, _("OLSR HNA")))


class OlsrRoutingTopologyMonitor(monitor_models.RoutingTopologyMonitor):
    """
    OLSR routing topology.
    """

    average_lq = models.FloatField(null=True)
    average_ilq = models.FloatField(null=True)
    average_etx = models.FloatField(null=True)

registration.point('node.monitoring').register_item(OlsrRoutingTopologyMonitor)


class OlsrRoutingTopologyMonitorStreams(ds_models.RegistryItemStreams):
    link_count = ds_fields.IntegerField(tags={
        'title': gettext_noop("Link count (OLSR)"),
        'description': gettext_noop("Number of links to other nodes in OLSR routing topology."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
        }
    })
    average_lq = ds_fields.FloatField(tags={
        'group': 'avg_link_quality',
        'title': gettext_noop("Average link quality"),
        'description': gettext_noop("Average OLSR link quality."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {'group': 'avg_link_quality', 'node': ds_fields.TagReference('node')},
        }
    })
    average_ilq = ds_fields.FloatField(tags={
        'group': 'avg_link_quality',
        'title': gettext_noop("Average inverse link quality"),
        'description': gettext_noop("Average OLSR inverse link quality."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {'group': 'avg_link_quality', 'node': ds_fields.TagReference('node')},
        }
    })
    average_etx = ds_fields.FloatField(tags={
        'title': gettext_noop("Average ETX"),
        'description': gettext_noop("Average OLSR ETX metric."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 1.0,
        }
    })

    def get_stream_query_tags(self):
        tags = super(OlsrRoutingTopologyMonitorStreams, self).get_stream_query_tags()
        tags.update({'link': None, 'protocol': 'olsr'})
        return tags

    def get_stream_tags(self):
        tags = super(OlsrRoutingTopologyMonitorStreams, self).get_stream_query_tags()
        tags.update({'link': None, 'protocol': 'olsr'})
        return tags

ds_pool.register(OlsrRoutingTopologyMonitor, OlsrRoutingTopologyMonitorStreams)


class OlsrTopologyLink(monitor_models.TopologyLink):
    """
    OLSR topology link.
    """

    lq = models.FloatField(default=0.0)
    ilq = models.FloatField(default=0.0)
    etx = models.FloatField(default=0.0)

    def get_link_attributes(self):
        """
        Returns additional link attributes that should be included in the
        topology link when it is transformed into a graph representation.
        """

        return {
            'lq': self.lq,
            'ilq': self.ilq,
            'etx': self.etx,
        }


def peer_name(text):
    return ds_fields.TagReference(transform=lambda m: text % {'peer_name': m.peer.config.core.general().name})


class OlsrTopologyLinkStreams(ds_models.ProxyRegistryItemStreams):
    lq = ds_fields.FloatField(tags={
        'group': 'link_quality',
        'title': peer_name(gettext_noop("Link quality to %(peer_name)s")),
        'description': gettext_noop("OLSR link quality."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {
                'group': 'link_quality',
                'link': ds_fields.TagReference('link'),
                'node': ds_fields.TagReference('node'),
            },
        }
    })
    ilq = ds_fields.FloatField(tags={
        'group': 'link_quality',
        'title': peer_name(gettext_noop("Inverse link quality to %(peer_name)s")),
        'description': gettext_noop("OLSR inverse link quality."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {
                'group': 'link_quality',
                'link': ds_fields.TagReference('link'),
                'node': ds_fields.TagReference('node'),
            },
        }
    })
    etx = ds_fields.FloatField(tags={
        'title': peer_name(gettext_noop("ETX to %(peer_name)s")),
        'description': gettext_noop("OLSR ETX metric for this link."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 1.0,
        }
    })

    def get_base(self, model):
        return model.monitor.cast()

    def get_stream_query_tags(self):
        tags = super(OlsrTopologyLinkStreams, self).get_stream_query_tags()
        tags.update({'link': self._model.peer.uuid, 'protocol': 'olsr'})
        return tags

    def get_stream_tags(self):
        tags = super(OlsrTopologyLinkStreams, self).get_stream_query_tags()
        tags.update({'link': self._model.peer.uuid, 'protocol': 'olsr'})
        return tags

ds_pool.register(OlsrTopologyLink, OlsrTopologyLinkStreams)


class OlsrRoutingAnnounceMonitor(monitor_models.RoutingAnnounceMonitor):
    """
    OLSR network announces.
    """

    pass

registration.point('node.monitoring').register_item(OlsrRoutingAnnounceMonitor)

from django.db import models
from django.utils.translation import ugettext as _, gettext_noop

from nodewatcher.core.monitor import models as monitor_models
from nodewatcher.core.registry import registration
from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

OLSR_PROTOCOL_NAME = 'olsr'

# Register the routing protocol option so interfaces can use it
registration.point('node.config').register_choice('core.interfaces#routing_protocol', OLSR_PROTOCOL_NAME, _("OLSR"))

# Register the subnet announce option so interfaces can use it
registration.point('node.config').register_choice('core.interfaces.network#routing_announce', OLSR_PROTOCOL_NAME, _("OLSR HNA"))


class OlsrRoutingTopologyMonitor(monitor_models.RoutingTopologyMonitor):
    """
    OLSR routing topology.
    """

    average_lq = models.FloatField(null=True)
    average_ilq = models.FloatField(null=True)
    average_etx = models.FloatField(null=True)

registration.point('node.monitoring').register_item(OlsrRoutingTopologyMonitor)


class OlsrRoutingTopologyMonitorStreams(ds_models.RegistryItemStreams):
    average_lq = ds_fields.FloatField(tags={
        'group': 'avg_link_quality',
        'description': gettext_noop("Average OLSR link quality."),
        'visualization': {
            'type': 'line',
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {'group': 'avg_link_quality', 'node': ds_fields.TagReference('node')},
        }
    })
    average_ilq = ds_fields.FloatField(tags={
        'group': 'avg_link_quality',
        'description': gettext_noop("Average OLSR inverse link quality."),
        'visualization': {
            'type': 'line',
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {'group': 'avg_link_quality', 'node': ds_fields.TagReference('node')},
        }
    })
    average_etx = ds_fields.FloatField(tags={
        'description': gettext_noop("Average OLSR ETX metric."),
        'visualization': {
            'type': 'line',
        }
    })

    def get_stream_query_tags(self):
        tags = super(OlsrRoutingTopologyMonitorStreams, self).get_stream_query_tags()
        tags.update({'link': None})
        return tags

    def get_stream_tags(self):
        tags = super(OlsrRoutingTopologyMonitorStreams, self).get_stream_query_tags()
        tags.update({'link': None})
        return tags

ds_pool.register(OlsrRoutingTopologyMonitor, OlsrRoutingTopologyMonitorStreams)


class OlsrTopologyLink(monitor_models.TopologyLink):
    """
    OLSR topology link.
    """

    lq = models.FloatField(default=0.0)
    ilq = models.FloatField(default=0.0)
    etx = models.FloatField(default=0.0)


class OlsrTopologyLinkStreams(ds_models.ProxyRegistryItemStreams):
    lq = ds_fields.FloatField(tags={
        'group': 'link_quality',
        'description': gettext_noop("OLSR link quality."),
        'visualization': {
            'type': 'line',
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
        'description': gettext_noop("OLSR inverse link quality."),
        'visualization': {
            'type': 'line',
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
        'description': gettext_noop("OLSR ETX metric for this link."),
        'visualization': {
            'type': 'line',
        }
    })

    def get_base(self, model):
        return model.monitor.cast()

    def get_stream_query_tags(self):
        tags = super(OlsrTopologyLinkStreams, self).get_stream_query_tags()
        tags.update({'link': self._model.peer.uuid})
        return tags

    def get_stream_tags(self):
        tags = super(OlsrTopologyLinkStreams, self).get_stream_query_tags()
        tags.update({'link': self._model.peer.uuid})
        return tags

ds_pool.register(OlsrTopologyLink, OlsrTopologyLinkStreams)


class OlsrRoutingAnnounceMonitor(monitor_models.RoutingAnnounceMonitor):
    """
    OLSR network announces.
    """

    pass

registration.point('node.monitoring').register_item(OlsrRoutingAnnounceMonitor)

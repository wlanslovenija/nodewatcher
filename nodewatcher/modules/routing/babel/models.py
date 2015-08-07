from django.db import models
from django.utils.translation import ugettext_lazy as _, gettext_noop

from nodewatcher.core.monitor import models as monitor_models
from nodewatcher.core.registry import registration, fields as registry_fields
from nodewatcher.modules.monitor.datastream import fields as ds_fields, models as ds_models
from nodewatcher.modules.monitor.datastream.pool import pool as ds_pool

BABEL_PROTOCOL_NAME = 'babel'

# Register the routing protocol option so interfaces can use it.
registration.point('node.config').register_choice('core.interfaces#routing_protocol', registration.Choice(BABEL_PROTOCOL_NAME, _("Babel")))

# Register the subnet announce option so interfaces can use it.
registration.point('node.config').register_choice('core.interfaces.network#routing_announce', registration.Choice(BABEL_PROTOCOL_NAME, _("Babel")))


class BabelRoutingTopologyMonitor(monitor_models.RoutingTopologyMonitor):
    """
    Babel routing topology.
    """

    router_id = models.CharField(max_length=64, null=True)
    average_rxcost = models.IntegerField(null=True)
    average_txcost = models.IntegerField(null=True)
    average_rttcost = models.IntegerField(null=True)
    average_cost = models.IntegerField(null=True)

registration.point('node.monitoring').register_item(BabelRoutingTopologyMonitor)


class LinkLocalAddress(models.Model):
    """
    A link-local address belonging to a Babel router.
    """

    router = models.ForeignKey(BabelRoutingTopologyMonitor, related_name='link_local')
    address = registry_fields.IPAddressField(host_required=True, db_index=True)
    interface = models.CharField(max_length=50, null=True)


class BabelRoutingTopologyMonitorStreams(ds_models.RegistryItemStreams):
    link_count = ds_fields.IntegerField(tags={
        'group': 'link_count',
        'title': gettext_noop("Link count (Babel)"),
        'description': gettext_noop("Number of links to other nodes in Babel routing topology."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'link_count', 'node': ds_fields.TagReference('node')},
        }
    })
    average_rxcost = ds_fields.IntegerField(tags={
        'group': 'avg_link_cost',
        'title': gettext_noop("Average RX link cost"),
        'description': gettext_noop("Average Babel RX link cost."),
        'visualization': {
            'type': 'line',
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'avg_link_cost', 'node': ds_fields.TagReference('node')},
        }
    })
    average_txcost = ds_fields.IntegerField(tags={
        'group': 'avg_link_cost',
        'title': gettext_noop("Average TX link cost"),
        'description': gettext_noop("Average Babel TX link cost."),
        'visualization': {
            'type': 'line',
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'avg_link_cost', 'node': ds_fields.TagReference('node')},
        }
    })
    average_rttcost = ds_fields.IntegerField(tags={
        'group': 'avg_link_cost',
        'title': gettext_noop("Average RTT link cost"),
        'description': gettext_noop("Average Babel RTT link cost."),
        'visualization': {
            'type': 'line',
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'with': {'group': 'avg_link_cost', 'node': ds_fields.TagReference('node')},
        }
    })
    average_cost = ds_fields.IntegerField(tags={
        'title': gettext_noop("Average cost"),
        'description': gettext_noop("Average Babel cost."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 1.0,
        }
    })

    def get_stream_query_tags(self):
        tags = super(BabelRoutingTopologyMonitorStreams, self).get_stream_query_tags()
        tags.update({'link': None, 'protocol': BABEL_PROTOCOL_NAME})
        return tags

    def get_stream_tags(self):
        tags = super(BabelRoutingTopologyMonitorStreams, self).get_stream_query_tags()
        tags.update({'link': None, 'protocol': BABEL_PROTOCOL_NAME})
        return tags

ds_pool.register(BabelRoutingTopologyMonitor, BabelRoutingTopologyMonitorStreams)


class BabelTopologyLink(monitor_models.TopologyLink):
    """
    Babel topology link.
    """

    interface = models.CharField(max_length=50, null=True)
    rxcost = models.IntegerField(default=0)
    txcost = models.IntegerField(default=0)
    rtt = models.IntegerField(default=0, null=True)
    rttcost = models.IntegerField(default=0, null=True)
    cost = models.IntegerField(default=0)
    # Reachability is not actually an integer but a bit field of 16 binary values,
    # representing a history of successfully received HELLOs. A value of 0 indicates
    # a lost packet, while a 1 indicates a successfully received packet.
    reachability = models.IntegerField(default=0)


def peer_name(text):
    return ds_fields.TagReference(transform=lambda m: text % {'peer_name': m.peer.config.core.general().name})


class BabelTopologyLinkStreams(ds_models.ProxyRegistryItemStreams):
    rxcost = ds_fields.IntegerField(tags={
        'group': 'link_cost',
        'title': peer_name(gettext_noop("RX cost to %(peer_name)s")),
        'description': gettext_noop("Babel link RX cost."),
        'visualization': {
            'type': 'line',
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {
                'group': 'link_cost',
                'link': ds_fields.TagReference('link'),
                'node': ds_fields.TagReference('node'),
            },
        }
    })
    txcost = ds_fields.IntegerField(tags={
        'group': 'link_cost',
        'title': peer_name(gettext_noop("TX cost to %(peer_name)s")),
        'description': gettext_noop("Babel link TX cost."),
        'visualization': {
            'type': 'line',
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {
                'group': 'link_cost',
                'link': ds_fields.TagReference('link'),
                'node': ds_fields.TagReference('node'),
            },
        }
    })
    rttcost = ds_fields.IntegerField(tags={
        'group': 'link_cost',
        'title': peer_name(gettext_noop("RTT cost to %(peer_name)s")),
        'description': gettext_noop("Babel link RTT cost."),
        'visualization': {
            'type': 'line',
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 0.0,
            'maximum': 1.0,
            'with': {
                'group': 'link_cost',
                'link': ds_fields.TagReference('link'),
                'node': ds_fields.TagReference('node'),
            },
        }
    })
    cost = ds_fields.IntegerField(tags={
        'title': peer_name(gettext_noop("Cost to %(peer_name)s")),
        'description': gettext_noop("Babel cost for this link."),
        'visualization': {
            'type': 'line',
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'minimum': 1.0,
        }
    })
    reachability = ds_fields.IntegerArrayNominalField(
        tags={
            'title': peer_name(gettext_noop("Reachability of %(peer_name)s")),
            'description': gettext_noop("Babel reachability for this link."),
            'visualization': {
                'type': 'heatmap',
                'hidden': True,
                'minimum': 0,
                'maximum': 1,
            }
        },
        # Convert the integer into a list of bit values. Also see model documentation.
        attribute=lambda model: [int(x) for x in list(bin(model.reachability & 0xFFFF | 0x10000)[3:])]
    )

    def get_base(self, model):
        return model.monitor.cast()

    def get_stream_query_tags(self):
        tags = super(BabelTopologyLinkStreams, self).get_stream_query_tags()
        tags.update({'link': self._model.peer.uuid, 'protocol': BABEL_PROTOCOL_NAME})
        return tags

    def get_stream_tags(self):
        tags = super(BabelTopologyLinkStreams, self).get_stream_query_tags()
        tags.update({'link': self._model.peer.uuid, 'protocol': BABEL_PROTOCOL_NAME})
        return tags

ds_pool.register(BabelTopologyLink, BabelTopologyLinkStreams)


class BabelRoutingAnnounceMonitor(monitor_models.RoutingAnnounceMonitor):
    """
    Babel network announces.
    """

    pass

registration.point('node.monitoring').register_item(BabelRoutingAnnounceMonitor)

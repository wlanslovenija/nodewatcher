from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import registration, fields as registry_fields
# Following import needed for 'node.monitoring' registration point
from nodewatcher.core.monitor import models as monitor_models


class StatusMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Node's status.
    """

    network = registry_fields.SelectorKeyField('node.monitoring', 'core.status#network', default='unknown')
    monitored = registry_fields.NullBooleanChoiceField('node.monitoring', 'core.status#monitored')
    health = registry_fields.SelectorKeyField('node.monitoring', 'core.status#health', default='unknown')

    class RegistryMeta:
        registry_id = 'core.status'

registration.point('node.monitoring').register_item(StatusMonitor)

# Register valid network states
registration.point('node.monitoring').register_choice(
    'core.status#network',
    registration.Choice('up', _("Up"), help_text=_("The node is reachable.")),
)
registration.point('node.monitoring').register_choice(
    'core.status#network',
    registration.Choice('down', _("Down"), help_text=_("The node is not connected to the network.")),
)
registration.point('node.monitoring').register_choice(
    'core.status#network',
    registration.Choice('visible', _("Visible"), help_text=_("The node is connected to the network but a network connection to it cannot be established.")),
)
registration.point('node.monitoring').register_choice(
    'core.status#network',
    registration.Choice('unknown', _("Unknown"), help_text=_("The network status of the node is unknown.")),
)

# Register valid monitored states
registration.point('node.monitoring').register_choice(
    'core.status#monitored',
    registration.Choice(True, _("Monitored"), help_text=_("The node is monitored by <i>nodewatcher</i>.")),
)
registration.point('node.monitoring').register_choice(
    'core.status#monitored',
    registration.Choice(False, _("Unmonitored"), help_text=_("The node is not monitored by <i>nodewatcher</i>.")),
)
registration.point('node.monitoring').register_choice(
    'core.status#monitored',
    registration.Choice(None, _("Unknown"), help_text=_("The monitored status of the node is unknown.")),
)

# Register valid health states
registration.point('node.monitoring').register_choice(
    'core.status#health',
    registration.Choice('healthy', _("Healthy"), help_text=_("No issues with the node have been detected."),),
)
registration.point('node.monitoring').register_choice(
    'core.status#health',
    registration.Choice('warnings', _("Warnings"), help_text=_("Minor issues with the node have been detected.")),
)
registration.point('node.monitoring').register_choice(
    'core.status#health',
    registration.Choice('errors', _("Errors"), help_text=_("Serious issues with the node have been detected.")),
)
registration.point('node.monitoring').register_choice(
    'core.status#health',
    registration.Choice('unknown', _("Unknown"), help_text=_("The health status of the node is unknown.")),
)

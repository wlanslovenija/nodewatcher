from django.utils.translation import ugettext as _

from nodewatcher.core.registry import registration, fields as registry_fields
# Following import needed for 'node.monitoring' registration point
from nodewatcher.core.monitor import models as monitor_models


class StatusMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Node's status.
    """

    network = registry_fields.RegistryChoiceField('node.monitoring', 'core.status#network', null=True)
    monitored = registry_fields.NullBooleanChoiceField('node.monitoring', 'core.status#monitored')
    health = registry_fields.RegistryChoiceField('node.monitoring', 'core.status#health', null=True)

    class RegistryMeta:
        registry_id = 'core.status'

registration.point('node.monitoring').register_item(StatusMonitor)

# Register valid network states
registration.point('node.monitoring').register_choice(
    'core.status#network',
    registration.Choice('up', _("Up"), help_text=_("The node is reachable."), icon='node-network-up'),
)
registration.point('node.monitoring').register_choice(
    'core.status#network',
    registration.Choice('down', _("Down"), help_text=_("The node is not connected to the network."), icon='node-network-down'),
)
registration.point('node.monitoring').register_choice(
    'core.status#network',
    registration.Choice('visible', _("Visible"), help_text=_("The node is connected to the network but a network connection to it cannot be established."), icon='node-network-visible'),
)
registration.point('node.monitoring').register_choice(
    'core.status#network',
    registration.Choice(None, _("Unknown"), help_text=_("The network status of the node is unknown."), icon='node-unknown'),
)

# Register valid monitored states
registration.point('node.monitoring').register_choice(
    'core.status#monitored',
    registration.Choice(True, _("Monitored"), help_text=_("The node is monitored by <i>nodewatcher</i>."), icon='node-monitoring-monitored'),
)
registration.point('node.monitoring').register_choice(
    'core.status#monitored',
    registration.Choice(False, _("Unmonitored"), help_text=_("The node is not monitored by <i>nodewatcher</i>."), icon='node-monitoring-unmonitored'),
)
registration.point('node.monitoring').register_choice(
    'core.status#monitored',
    registration.Choice(None, _("Unknown"), help_text=_("The monitored status of the node is unknown."), icon='node-unknown'),
)

# Register valid health states
registration.point('node.monitoring').register_choice(
    'core.status#health',
    registration.Choice('healthy', _("Healthy"), help_text=_("No issues with the node have been detected."), icon='node-health-healthy'),
)
registration.point('node.monitoring').register_choice(
    'core.status#health',
    registration.Choice('warnings', _("Warnings"), help_text=_("Minor issues with the node have been detected."), icon='node-health-warnings'),
)
registration.point('node.monitoring').register_choice(
    'core.status#health',
    registration.Choice('errors', _("Errors"), help_text=_("Serious issues with the node have been detected."), icon='node-health-errors'),
)
registration.point('node.monitoring').register_choice(
    'core.status#health',
    registration.Choice(None, _("Unknown"), help_text=_("The health status of the node is unknown."), icon='node-unknown'),
)

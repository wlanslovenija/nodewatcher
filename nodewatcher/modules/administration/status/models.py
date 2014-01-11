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
    monitored = models.NullBooleanField()
    health = registry_fields.SelectorKeyField('node.monitoring', 'core.status#health', default='unknown')

    class RegistryMeta:
        registry_id = 'core.status'

registration.point('node.monitoring').register_item(StatusMonitor)

# Register valid network states
registration.point('node.monitoring').register_choice('core.status#network', registration.Choice('up', _("Up")))
registration.point('node.monitoring').register_choice('core.status#network', registration.Choice('down', _("Down")))
registration.point('node.monitoring').register_choice('core.status#network', registration.Choice('visible', _("Visible")))
registration.point('node.monitoring').register_choice('core.status#network', registration.Choice('unknown', _("Unknown")))

# Register valid health states
registration.point('node.monitoring').register_choice('core.status#health', registration.Choice('healthy', _("Healthy")))
registration.point('node.monitoring').register_choice('core.status#health', registration.Choice('warnings', _("Warnings")))
registration.point('node.monitoring').register_choice('core.status#health', registration.Choice('errors', _("Errors")))
registration.point('node.monitoring').register_choice('core.status#health', registration.Choice('unknown', _("Unknown")))

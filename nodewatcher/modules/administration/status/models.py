from django.db import models
from django.utils.translation import ugettext as _

from nodewatcher.core.registry import registration, fields as registry_fields
# Following import needed for 'node.monitoring' registration point
from nodewatcher.core.monitor import models as monitor_models


class StatusMonitor(registration.bases.NodeMonitoringRegistryItem):
    """
    Node's status.
    """

    network = registry_fields.SelectorKeyField('node.monitoring', 'core.status#network')
    monitored = models.NullBooleanField(null=True)
    health = registry_fields.SelectorKeyField('node.monitoring', 'core.status#health')

    class RegistryMeta:
        registry_id = 'core.status'

registration.point('node.monitoring').register_item(StatusMonitor)

# Register valid network states
registration.point('node.monitoring').register_choice('core.status#network', 'up', _("Up"))
registration.point('node.monitoring').register_choice('core.status#network', 'down', _("Down"))
registration.point('node.monitoring').register_choice('core.status#network', 'visible', _("Visible"))
registration.point('node.monitoring').register_choice('core.status#network', 'unknown', _("Unknown"))

# Register valid health states
registration.point('node.monitoring').register_choice('core.status#health', 'errors', _("Errors"))
registration.point('node.monitoring').register_choice('core.status#health', 'warnings', _("Warnings"))
registration.point('node.monitoring').register_choice('core.status#health', 'healthy', _("Healthy"))
registration.point('node.monitoring').register_choice('core.status#health', 'unknown', _("Unknown"))

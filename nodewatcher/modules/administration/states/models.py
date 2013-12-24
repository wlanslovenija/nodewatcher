from django.utils.translation import ugettext as _

from nodewatcher.core.registry import registration
# Following import needed for 'node.monitoring' registration point
from nodewatcher.core.monitor import models as monitor_models

# Register valid states
registration.point('node.monitoring').register_choice('core.status#status', 'up', _("Up"))
registration.point('node.monitoring').register_choice('core.status#status', 'down', _("Down"))
registration.point('node.monitoring').register_choice('core.status#status', 'visible', _("Visible"))
registration.point('node.monitoring').register_choice('core.status#status', 'pending', _("Pending"))

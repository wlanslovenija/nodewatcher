from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.frontend import components


def device_context(context):
    general = context['node'].config.core.general()
    if not hasattr(general, 'get_device'):
        return {'device': _("unknown")}

    device = general.get_device()
    if not device:
        return {'device': _("unknown")}

    return {
        'device': device.get_display_name()
    }

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='device',
    template='nodes/cgm/device.html',
    weight=80,
    extra_context=device_context,
))

# Provide statistics only in case the nodewatcher.modules.frontend.statistics app is installed.
if apps.is_installed('nodewatcher.modules.frontend.statistics'):
    from nodewatcher.modules.frontend.statistics.pool import pool as statistics_pool
    from . import statistics

    statistics_pool.register(statistics.NodesByDeviceResource())

    components.partials.get_partial('network_statistics_partial').add(components.PartialEntry(
        name='cgm',
        template='network/statistics/cgm.html',
        weight=60,
    ))

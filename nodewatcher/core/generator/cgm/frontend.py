from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.api import urls as api_urls
from nodewatcher.core.frontend import components

from . import views


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

api_urls.v2_api.register('statistics/device', views.DeviceStatisticsViewSet, base_name='statistics-device')

components.partials.get_partial('node_general_partial').add(components.PartialEntry(
    name='device',
    template='nodes/cgm/device.html',
    weight=80,
    extra_context=device_context,
))

components.partials.get_partial('network_statistics_partial').add(components.PartialEntry(
    name='cgm',
    template='network/statistics/cgm.html',
    weight=60,
))

from django.apps import apps

from nodewatcher.core.frontend import components


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

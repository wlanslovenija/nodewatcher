from django.dispatch import receiver

from nodewatcher.core.allocation.ip import signals

from . import models

@receiver(signals.filter_pools)
def filter_pools(sender, pool, cfg, **kwargs):
    """
    Project-based pool selection.
    """

    try:
        # Only list the pools that are available for the selected project
        pool.queryset = pool.queryset.filter(
            projects = cfg['core.project'][0].project
        )
    except (models.Project.DoesNotExist, KeyError, AttributeError):
        pass

from django.db import models
from nodewatcher.core.monitor import models as monitor_models


class NodeChannel(models.Model):

    interface = models.ForeignKey(
        monitor_models.WifiInterfaceMonitor,
        on_delete=models.CASCADE,
    )
    channel_width = models.PositiveIntegerField()
    optimal_start_frequency = models.PositiveIntegerField()
    optimal_channel_width = models.PositiveIntegerField()
    optimal_channel_interference = models.PositiveIntegerField()

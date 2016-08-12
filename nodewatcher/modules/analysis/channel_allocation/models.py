from django.db import models
from nodewatcher.core.monitor import models as monitor_models


class NodeChannel(models.Model):

    interface = models.ForeignKey(
        monitor_models.WifiInterfaceMonitor,
        on_delete=models.CASCADE,
    )
    optimal_channel = models.PositiveIntegerField()
    channel_width = models.PositiveIntegerField()


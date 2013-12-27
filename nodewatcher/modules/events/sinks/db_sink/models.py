from django.db import models

import json_field

from nodewatcher.core import models as core_models


class SerializedNodeEvent(models.Model):
    """
    A serialized version of node events.
    """

    timestamp = models.DateTimeField()
    related_nodes = models.ManyToManyField(core_models.Node, related_name='events')
    severity = models.IntegerField()
    title = models.CharField(max_length=200)
    source_name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=200)
    description = models.TextField(null=True)
    record = json_field.JSONField()

    def get_event_class(self):
        """
        Returns the event class associated with this event.
        """

        # TODO
        pass

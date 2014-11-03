from django.db import models
from django.contrib.auth import models as auth_models

import json_field

from nodewatcher.core import models as core_models
from nodewatcher.core.events import pool


class SerializedNodeEvent(models.Model):
    """
    A serialized version of node events.
    """

    timestamp = models.DateTimeField()
    related_nodes = models.ManyToManyField(core_models.Node, related_name='events')
    related_users = models.ManyToManyField(auth_models.User, related_name='events')
    severity = models.IntegerField()
    source_name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=200)
    record = json_field.JSONField()

    @property
    def description(self):
        """
        Returns a localized event description.
        """

        return self.get_event_class().get_description(self.record)

    def get_event_class(self):
        """
        Returns the event class associated with this event.
        """

        return pool.get_record(self.source_name, self.source_type)

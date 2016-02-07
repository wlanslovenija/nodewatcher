from django.db import models
from django.contrib.auth import models as auth_models

import jsonfield

from nodewatcher.core import models as core_models
from nodewatcher.core.events import pool


class SerializedEvent(models.Model):
    """
    Base class for serialized events.
    """

    severity = models.IntegerField()
    source_name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=200)
    record = jsonfield.JSONField(null=True)

    class Meta:
        abstract = True

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


class SerializedNodeEvent(SerializedEvent):
    """
    A serialized version of node events.
    """

    timestamp = models.DateTimeField()
    related_nodes = models.ManyToManyField(core_models.Node, related_name='events')
    related_users = models.ManyToManyField(auth_models.User, related_name='events')


class SerializedNodeWarning(SerializedEvent):
    """
    A serialized version of node warnings.
    """

    uuid = models.UUIDField(primary_key=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    related_nodes = models.ManyToManyField(core_models.Node, related_name='warnings')

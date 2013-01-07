import uuid

from django.db import models

class Node(models.Model):
    """
    This class represents a single node in the network.
    """
    uuid = models.CharField(max_length = 40, primary_key = True)

    def save(self, **kwargs):
        """
        Override save so we can generate UUIDs.
        """
        if not self.uuid:
            self.pk = str(uuid.uuid4())

        super(Node, self).save(**kwargs)

    def __unicode__(self):
        """
        Returns a string representation of this node.
        """
        return self.uuid

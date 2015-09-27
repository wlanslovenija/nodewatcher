from django.db import models

import json_field


class UnknownNode(models.Model):
    """
    A record describing a node that is not yet in the database, but which has
    been discovered somehow in the network.
    """

    uuid = models.CharField(max_length=40, primary_key=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, unpack_ipv4=True)
    certificate = json_field.JSONField(null=True)

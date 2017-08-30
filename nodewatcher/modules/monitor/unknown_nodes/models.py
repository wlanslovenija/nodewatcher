from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UnknownNode(models.Model):
    """
    A record describing a node that is not yet in the database, but which has
    been discovered somehow in the network.
    """

    # Possible origins.
    PUSH = 'push'
    UNKNOWN = 'unknown'
    ORIGIN_CHOICES = (
        (PUSH, _("Push")),
        (UNKNOWN, _("Unknown")),
    )

    uuid = models.CharField(max_length=40, primary_key=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, unpack_ipv4=True)
    certificate = JSONField(null=True)
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES, default=UNKNOWN)

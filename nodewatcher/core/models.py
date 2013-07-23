import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .registry import fields as registry_fields, registration


class Node(models.Model):
    """
    This class represents a single node in the network.
    """

    uuid = models.CharField(max_length=40, primary_key=True)

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

# Create registration point
registration.create_point(Node, 'config')


class GeneralConfig(registration.bases.NodeConfigRegistryItem):
    """
    General node configuration containing basic parameters about the
    node.
    """

    name = models.CharField(max_length=30)

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 1
        registry_id = 'core.general'
        registry_section = _("General Configuration")
        registry_name = _("Basic Configuration")
        lookup_proxies = ['name']

# TODO: Validate node name via regexp: NODE_NAME_RE = re.compile(r'^[a-z](?:-?[a-z0-9]+)*$')

registration.point('node.config').register_item(GeneralConfig)


class RouterIdConfig(registration.bases.NodeConfigRegistryItem):
    """
    Router identifier configuration.
    """

    router_id = models.CharField(max_length=100)
    family = registry_fields.SelectorKeyField('node.config', 'core.routerid#family')

    class Meta:
        app_label = 'core'

    class RegistryMeta:
        form_order = 100
        registry_id = 'core.routerid'
        multiple = True
        hidden = True

registration.point('node.config').register_choice('core.routerid#family', 'ipv4', _("IPv4"))
registration.point('node.config').register_choice('core.routerid#family', 'ipv6', _("IPv6"))
registration.point('node.config').register_item(RouterIdConfig)

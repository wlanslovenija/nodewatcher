from django.db import models
from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.registry import fields as registry_fields, registration


class IdentityConfig(registration.bases.NodeConfigRegistryItem):
    """
    Configuration of node identity verification.
    """

    trust_policy = registry_fields.RegistryChoiceField('node.config', 'core.identity#trust_policy', default='first')
    store_unknown = models.BooleanField(
        verbose_name=_("Store Unknown Identities"),
        help_text=_("Set in order for unknown identities to be stored, so you may later confirm them. Until they are confirmed, they are not trusted."),
        default=True,
    )

    class RegistryMeta:
        form_weight = 7
        registry_id = 'core.identity'
        registry_section = _("Node Identity")
        registry_name = _("Basic Identity")

registration.point('node.config').register_choice('core.identity#trust_policy', registration.Choice('any', _("Trust any identity (INSECURE)")))
registration.point('node.config').register_choice('core.identity#trust_policy', registration.Choice('first', _("Trust and store the first received identity")))
registration.point('node.config').register_choice('core.identity#trust_policy', registration.Choice('config', _("Only trust explicitly configured identities")))
registration.point("node.config").register_item(IdentityConfig)


class IdentityMechanismConfig(registration.bases.NodeConfigRegistryItem):
    """
    Configuration of node identity verification mechanisms.
    """

    identity = registry_fields.IntraRegistryForeignKey(
        IdentityConfig, editable=False, null=False, related_name='mechanisms'
    )

    trusted = models.BooleanField(default=False)
    automatically_added = models.BooleanField(default=False, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True, editable=False)

    class RegistryMeta:
        form_weight = 7
        registry_id = 'core.identity.mechanisms'
        registry_section = _("Identity Mechanisms")
        registry_name = _("Null Mechanism")
        multiple = True
        hidden = True

    def is_match(self, data):
        """
        This method must be overriden by subclasses. It should return True if
        the mechanism-dependent data is a match for this identity.

        :param data: Mechanism-dependent data
        :return: True if data is a match for this identity
        """

        raise NotImplementedError

    @classmethod
    def from_data(cls, data):
        """
        This method must be overriden by subclasses. It should return any arguments
        to the class constructor that will result in constructing an instance which
        will match the passed data.

        :param data: Mechanism-dependent data
        :return: A dictionary of constructor arguments
        """

        raise NotImplementedError

registration.point('node.config').register_subitem(IdentityConfig, IdentityMechanismConfig)

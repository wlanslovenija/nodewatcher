import datetime

from django.apps import apps
from django.contrib.postgres import fields as postgres_fields
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from polymorphic import models as polymorphic_models

from nodewatcher.core import validators as core_validators
from nodewatcher.core.registry import fields as registry_fields, registration
from nodewatcher.core.generator.cgm import models as cgm_models


class SNMPDaemonConfig(cgm_models.PackageConfig):
    """
    SNMP Daemon configuration.
    """

    community = models.CharField(max_length=100, verbose_name=_("SNMP Community"))
    location = models.CharField(max_length=100, verbose_name=_("Device location"))
    contact = models.CharField(max_length=100, verbose_name=_("Contact"))

    class RegistryMeta(cgm_models.PackageConfig.RegistryMeta):
        registry_name = _("SNMP Daemon")

registration.point('node.config').register_item(SNMPDaemonConfig)

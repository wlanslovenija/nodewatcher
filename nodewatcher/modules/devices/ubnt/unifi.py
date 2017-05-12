from django.utils.translation import ugettext_lazy as _

from nodewatcher.core.generator.cgm import base as cgm_base, protocols as cgm_protocols, devices as cgm_devices


class UBNTUapACLite(cgm_devices.DeviceBase):
    """
    UBNT UAP AC Lite device descriptor.
    """

    identifier = 'ub-uap-ac-lite'
    name = "Unifi AP AC Lite"
    manufacturer = "Ubiquiti"
    url = 'http://www.ubnt.com/'
    architecture = 'ar71xx'

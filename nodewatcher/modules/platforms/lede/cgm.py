from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base
from nodewatcher.modules.platforms.openwrt import cgm as openwrt_cgm

from . import builder as lede_builder


class PlatformLEDE(openwrt_cgm.PlatformOpenWRT):
    """
    LEDE platform descriptor.
    """

    builder_class = lede_builder.Builder

    def get_profile(self, device):
        """
        Returns the device profile.
        """

        if 'lede' in device.profiles:
            return device.profiles['lede']

        return device.profiles['openwrt']


# Register the LEDE platform and include all modules for OpenWRT platform.
cgm_base.register_platform('lede', _("LEDE"), PlatformLEDE(), include=['openwrt'])

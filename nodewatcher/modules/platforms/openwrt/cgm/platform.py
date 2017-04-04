from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base

from .. import builder as openwrt_builder
from .. import configuration


class PlatformOpenWRT(cgm_base.PlatformBase):
    """
    OpenWRT platform descriptor.
    """

    config_class = configuration.UCIConfiguration
    builder_class = openwrt_builder.Builder

    def get_profile(self, device):
        """
        Returns the device profile.
        """

        return device.profiles['openwrt']

    def build(self, result):
        """
        Builds the firmware using a previously generated and properly
        formatted configuration.

        :param result: Destination build result
        :return: A list of generated firmware files
        """

        # Extract the device descriptor to get the profile.
        device = result.node.config.core.general().get_device()
        profile = self.get_profile(device)

        builder = self.builder_class(result, profile)
        return builder.build()

cgm_base.register_platform('openwrt', _("OpenWRT"), PlatformOpenWRT())

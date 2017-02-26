import os

from nodewatcher.modules.platforms.openwrt import builder as openwrt_builder


class Builder(openwrt_builder.Builder):
    """
    Firmware builder wrapper.
    """

    def get_base_output_dir(self):
        """
        Determine the location of output files.
        """

        base_dir = os.path.join('bin', 'targets')
        targets = self._builder.list_dir(base_dir)
        return os.path.join(base_dir, targets[0])

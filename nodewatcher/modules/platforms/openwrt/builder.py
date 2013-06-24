import os, tempfile, shutil, subprocess

from django.conf import settings

from nodewatcher.core.generator.cgm import base as cgm_base

def build_image(cfg, arch, version, profile, packages):
    """
    Spawns the builder process for the specified firmware image.

    :param cfg: Generated configuration (per file format)
    :param arch: Device OpenWRT architecture
    :param version: Builder version
    :param profile: Device OpenWRT profile
    :param packages: A list of OpenWRT packages to install
    :return: A list of output firmware files
    """

    # Allocate a temporary directory
    temp_path = tempfile.mkdtemp()

    try:
        # Prepare configuration files
        cfg_path = os.path.join(temp_path, 'etc', 'config')
        os.makedirs(cfg_path)
        for fname, content in cfg.items():
            cfile = open(os.path.join(cfg_path, fname), 'w')
            cfile.write(content)
            cfile.close()

        # Change the working directory to the proper architecture path
        try:
            arch_path = os.path.join(
                settings.GENERATOR_BUILDERS['openwrt']['directory'],
                settings.GENERATOR_BUILDERS['openwrt']['versions'][version][0],
                arch
            )
            os.chdir(arch_path)
        except KeyError:
            # Specified version or OpenWRT platform not configured
            raise cgm_base.BuildError
        except OSError:
            # Specified builder directory does not exist
            raise cgm_base.BuildError

        # Run the build system and wait for its completion
        try:
            subprocess.check_call([
                'make', 'image',
                'PROFILE=%s' % profile["name"],
                'FILES=%s' % temp_path,
                'PACKAGES=%s' % " ".join(packages)
            ])
        except subprocess.CalledProcessError:
            raise cgm_base.BuildError

        # Collect the output files and return them
        fw_files = [
            os.path.join(arch_path, 'bin', arch, fw_file)
            for fw_file in profile['files']
        ]

        return fw_files
    finally:
        # Remove the temporary directory
        shutil.rmtree(temp_path)

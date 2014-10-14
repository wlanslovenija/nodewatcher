import os


def build_image(result, profile):
    """
    Spawns the builder process for the specified firmware image.

    :param result: Destination build result
    :param profile: Device OpenWRT profile
    :return: A list of output firmware files
    """

    cfg = result.config

    with result.builder.connect() as builder:
        temp_path = builder.create_tempdir()

        # Prepare configuration files
        cfg_path = os.path.join(temp_path, 'etc', 'config')
        for fname, content in cfg.items():
            if fname.startswith('_'):
                continue
            builder.write_file(os.path.join(cfg_path, fname), content)

        # Run the build system and wait for its completion
        result.build_log = builder.call(
            'make', 'image',
            'PROFILE=%s' % profile["name"],
            'FILES=%s' % temp_path,
            'PACKAGES=%s' % " ".join(cfg['_packages'])
        )

        # Collect the output files and return them
        fw_files = [
            (fw_file, builder.read_result_file(os.path.join('bin', result.builder.architecture, fw_file)))
            for fw_file in profile['files']
        ]

        return fw_files

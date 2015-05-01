import io
import os

from nodewatcher.core.generator.cgm import exceptions as cgm_exceptions


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

        # Prepare configuration files.
        cfg_path = os.path.join(temp_path, 'etc', 'config')
        for fname, content in cfg.items():
            if fname.startswith('_'):
                continue
            builder.write_file(os.path.join(cfg_path, fname), content)

        # Prepare user account files.
        from . import crypt
        passwd = io.StringIO()
        for account in cfg['_accounts'].get('users', {}).values():
            if account['password'] != '*':
                account['password'] = crypt.md5crypt(
                    account['password'],
                    os.urandom(6).encode('base_64').strip()
                )

            passwd.write('%(username)s:%(password)s:%(uid)d:%(gid)d:%(username)s:%(home)s:%(shell)s\n' % account)
        builder.write_file(os.path.join(temp_path, 'etc', 'passwd'), passwd.getvalue().encode('ascii'))

        # Prepare the banner file if configured.
        if cfg.get('_banner', None):
            banner = io.StringIO()
            banner.write(cfg['_banner'])
            builder.write_file(os.path.join(temp_path, 'etc', 'banner'), banner.getvalue().encode('ascii'))

        # Prepare the routing table mappings.
        tables = io.StringIO()
        for identifier, name in cfg['_routing_tables'].items():
            tables.write('%s\t%s\n' % (identifier, name))
        builder.write_file(os.path.join(temp_path, 'etc', 'iproute2', 'rt_tables'), tables.getvalue().encode('ascii'))

        # Prepare the crypto objects.
        for crypto_object in cfg['_crypto']:
            if not crypto_object['path']:
                continue

            builder.write_file(os.path.join(temp_path, crypto_object['path'][1:]), crypto_object['content'].encode('ascii'))

        # Run the build system and wait for its completion.
        result.build_log = builder.call(
            'make', 'image',
            'PROFILE=%s' % profile["name"],
            'FILES=%s' % temp_path,
            'PACKAGES=%s' % " ".join(cfg['_packages'])
        )

        # Collect the output files and return them.
        fw_files = []
        for fw_file in profile['files']:
            try:
                fw_files.append(
                    (fw_file, builder.read_result_file(os.path.join('bin', result.builder.architecture, fw_file)))
                )
            except IOError:
                raise cgm_exceptions.BuildError('Output file \'%s\' not found!' % fw_file)

        return fw_files

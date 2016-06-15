import base64
import io
import os

from nodewatcher.core.generator.cgm import base as cgm_base, exceptions as cgm_exceptions


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

        # Prepare the sysctl configuration.
        if cfg.get('_sysctl', None):
            sysctl = io.StringIO()
            for key, value in cfg['_sysctl'].items():
                sysctl.write('%s=%s\n' % (key, value))
            builder.write_file(os.path.join(temp_path, 'etc', 'sysctl.conf'), sysctl.getvalue().encode('ascii'))

        # Prepare the routing table mappings.
        tables = io.StringIO()
        for identifier, name in cfg['_routing_tables'].items():
            tables.write('%s\t%s\n' % (identifier, name))
        builder.write_file(os.path.join(temp_path, 'etc', 'iproute2', 'rt_tables'), tables.getvalue().encode('ascii'))

        # Prepare the crypto objects.
        ssh_authorized_keys = io.StringIO()
        for crypto_object in cfg['_crypto']:
            # Populate SSH authorized keys.
            if crypto_object['type'] == cgm_base.PlatformCryptoManager.SSH_AUTHORIZED_KEY:
                ssh_authorized_keys.write('%s\n' % crypto_object['content'])

            if not crypto_object['path']:
                continue

            content = crypto_object['content']
            if crypto_object['decoder'] == cgm_base.PlatformCryptoManager.BASE64:
                content = base64.b64decode(content)
            else:
                content = content.encode('ascii')

            builder.write_file(os.path.join(temp_path, crypto_object['path'][1:]), content)

        builder.write_file(
            os.path.join(temp_path, 'etc', 'dropbear', 'authorized_keys'),
            ssh_authorized_keys.getvalue().encode('ascii'),
            mode=0600,
        )

        builder.chmod(os.path.join(temp_path, 'etc', 'dropbear'), 0755)

        # Prepare any custom files.
        for path, custom_file in cfg['_files'].items():
            if path[0] == '/':
                path = path[1:]

            builder.write_file(
                os.path.join(temp_path, path),
                custom_file['content'].encode('utf8'),
                mode=custom_file['mode'],
            )

        # Clean the build first to prevent accidentally taking build results from a previous build.
        builder.call('make', 'clean')
        # Ensure the prerequisite check is skipped.
        builder.call('touch', 'staging_dir/host/.prereq-build')

        # Run the build system and wait for its completion.
        result.build_log = builder.call(
            'make', 'image',
            'PROFILE=%s' % profile["name"],
            'FILES=%s' % temp_path,
            'PACKAGES=%s' % " ".join(cfg['_packages']),
            'FORCE=1'
        )

        # Determine the location of output files.
        output_locations = builder.list_dir('bin')

        # Collect the output files and return them.
        fw_files = []
        for fw_file in profile['files']:
            for output_location in output_locations:
                try:
                    fw_files.append(
                        (fw_file, builder.read_result_file(os.path.join('bin', output_location, fw_file)))
                    )
                    break
                except IOError:
                    continue
            else:
                raise cgm_exceptions.BuildError('Output file \'%s\' not found!' % fw_file)

        return fw_files

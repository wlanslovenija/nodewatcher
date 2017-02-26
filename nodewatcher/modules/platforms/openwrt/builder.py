import base64
import fnmatch
import io
import os

from nodewatcher.core.generator.cgm import base as cgm_base, exceptions as cgm_exceptions


class Builder(object):
    """
    Firmware builder wrapper.
    """

    def __init__(self, result, profile):
        """
        Construct a builder.

        :param result: Destination build result
        :param profile: Device profile
        """

        self.result = result
        self.profile = profile
        self._builder = None
        self._path = None

    def build(self):
        """
        Run the build process.

        :return: A list of output firmware files
        """

        with self.result.builder.connect() as builder:
            self._builder = builder

            try:
                self.prepare_files()
                self.prepare_clean()
                self.run_build()
                return self.extract_files()
            finally:
                self._builder = None
                self._path = None

    def prepare_files(self):
        """
        Prepare files.
        """

        cfg = self.result.config
        builder = self._builder

        temp_path = builder.create_tempdir()
        self._path = temp_path

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

    def prepare_clean(self):
        """
        Prepare a clean build environment.
        """

        # Clean the build first to prevent accidentally taking build results from a previous build.
        self._builder.call('make', 'clean')
        # Ensure build dir paths are cleaned. This is required because for some architectures, there
        # are leftovers even after a 'make clean'.
        self._builder.call('rm', '-rf', 'build_dir/target-*/linux-*/{tmp,root.squashfs}', quote=False)
        # Ensure the prerequisite check is skipped.
        self._builder.call('touch', 'staging_dir/host/.prereq-build')

    def run_build(self):
        """
        Run the build system and wait for its completion.
        """

        self.result.build_log = self._builder.call(
            'make', 'image',
            'PROFILE=%s' % self.profile["name"],
            'FILES=%s' % self._path,
            'PACKAGES=%s' % " ".join(self.result.config['_packages']),
            'FORCE=1'
        )

    def get_base_output_dir(self):
        """
        Determine the location of output files.
        """

        return 'bin'

    def extract_files(self):
        """
        Extract built files.
        """

        base_dir = self.get_base_output_dir()
        output_locations = self._builder.list_dir(base_dir)

        # Collect the output files and return them.
        fw_files = []
        for fw_file in self.profile['files']:
            matched = False
            for output_location in output_locations:
                for output_filename in self._builder.list_dir(os.path.join(base_dir, output_location)):
                    if fnmatch.fnmatch(output_filename, fw_file):
                        try:
                            fw_files.append((
                                output_filename,
                                self._builder.read_result_file(os.path.join(base_dir, output_location, output_filename))
                            ))
                            matched = True
                        except IOError:
                            continue

            if not matched:
                raise cgm_exceptions.BuildError('Output file \'%s\' not found!' % fw_file)

        return fw_files

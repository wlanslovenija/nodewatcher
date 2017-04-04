from nodewatcher.core.generator.cgm import base as cgm_base

from . import uci

# Support different versions of libapt bindings.
try:
    import apt_pkg
    apt_pkg.init()
    apt_version_compare = apt_pkg.version_compare
except ImportError:
    try:
        import apt
        apt_version_compare = apt.VersionCompare
    except (ImportError, AttributeError):
        apt_version_compare = None


class OpenWrtCryptoManager(cgm_base.PlatformCryptoManager):
    class CryptoObject(cgm_base.PlatformCryptoManager.CryptoObject):
        def __init__(self, *args, **kwargs):
            super(OpenWrtCryptoManager.CryptoObject, self).__init__(*args, **kwargs)

            # If path is never requested, we will not generate a file at all.
            self._path = None

        def path(self):
            """
            Returns the path to the crypto object.
            """

            type_map = {
                cgm_base.PlatformCryptoManager.CERTIFICATE: 'certificate',
                cgm_base.PlatformCryptoManager.PUBLIC_KEY: 'public_key',
                cgm_base.PlatformCryptoManager.PRIVATE_KEY: 'private_key',
                cgm_base.PlatformCryptoManager.SYMMETRIC_KEY: 'symmetric_key',
                cgm_base.PlatformCryptoManager.SSH_AUTHORIZED_KEY: 'ssh_authorized_key',
            }
            self._path = '/etc/crypto/%s/%s' % (type_map[self.object_type], self.name)
            return self._path

        def get_config(self):
            """
            Returns a configuration dictionary suitable for use in JSON
            documents.
            """

            config = super(OpenWrtCryptoManager.CryptoObject, self).get_config()
            config.update({
                'path': self._path,
            })

            return config

    object_class = CryptoObject


class OpenWrtSysctlManager(object):
    """
    OpenWrt-specific sysctl manager.
    """

    def __init__(self):
        """
        Class constructor.
        """

        self._settings = {}

    def set_variable(self, key, value):
        """
        Sets a sysctl variable.

        :param key: Variable key
        :param value: Variable value
        """

        self._settings[key] = value

    def get_config(self):
        """
        Returns sysctl configuration suitable for use in JSON documents.
        """

        return self._settings


class UCIConfiguration(cgm_base.PlatformConfiguration):
    """
    An in-memory implementation of UCI configuration.
    """

    crypto_manager_class = OpenWrtCryptoManager
    sysctl_manager_class = OpenWrtSysctlManager

    def __init__(self, *args, **kwargs):
        """
        Class constructor.
        """

        super(UCIConfiguration, self).__init__(*args, **kwargs)
        self.sysctl = self.sysctl_manager_class()
        self._packages = {}

    def sanitize_identifier(self, identifier):
        """
        Sanitizes an identifier so that it is appropriate for use as an
        UCI identifier. This should be used for any external strings, which
        are used as UCI identifiers (option or section names).

        :param identifier: Potentially "dirty" identifier
        :return: An identifier suitable for use in UCI
        """

        return uci.UCI_IDENTIFIER_REPLACE.sub('_', identifier)

    def package_version_compare(self, version_a, version_b):
        """
        Platform-specific version check. Should return an integer, which is
        less than, equal to or greater than zero, based on the result of the
        comparison.

        :param version_a: First version
        :param version_b: Second version
        """

        if apt_version_compare is not None:
            return apt_version_compare(version_a, version_b)
        else:
            raise NotImplementedError('Version comparison functions are not available.')

    def get_build_config(self):
        """
        Returns a build configuration which must be JSON-serializable. This
        configuration will be passed to the backend builder function and must
        contain anything that the builder will need to configure the generated
        firmware.
        """

        result = self.format(fmt=uci.UCIFormat.FILES)
        result.update(super(UCIConfiguration, self).get_build_config())
        result.update({
            '_sysctl': self.sysctl.get_config(),
        })
        return result

    def __getattr__(self, package):
        """
        Returns the desired UCI package (config file).
        """

        if package.startswith('__') and package.endswith('__'):
            raise AttributeError(package)

        return self._packages.setdefault(package, uci.UCIPackage(package))

    __getitem__ = __getattr__

    def format(self, fmt=uci.UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.

        :param fmt: Wanted export format
        """

        if fmt == uci.UCIFormat.DUMP:
            # UCI dump format.
            output = []
            for name, package in self._packages.iteritems():
                output += package.format(fmt=fmt)
        elif fmt == uci.UCIFormat.FILES:
            # UCI split into multiple files.
            output = {}
            for name, package in self._packages.iteritems():
                output[name] = '\n'.join(package.format(fmt=fmt))

        return output

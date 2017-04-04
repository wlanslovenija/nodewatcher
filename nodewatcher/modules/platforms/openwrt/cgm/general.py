from django.conf import settings
from django.utils import crypto
from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base, models as cgm_models
from nodewatcher.core.registry import exceptions as registry_exceptions
from nodewatcher.utils import posix_tz


@cgm_base.register_platform_module('openwrt', 10)
def general(node, cfg):
    """
    General configuration for nodewatcher firmware.
    """

    system = cfg.system.add('system')
    system.hostname = node.config.core.general().name
    system.uuid = node.uuid
    # Enable bigger logs by default.
    system.log_size = 256

    try:
        zone = node.config.core.location().timezone.zone
        system.timezone = posix_tz.get_posix_tz(zone)
        if not system.timezone:
            raise cgm_base.ValidationError(_("Unsupported OpenWRT timezone '%s'!") % zone)
    except (registry_exceptions.RegistryItemNotRegistered, AttributeError):
        system.timezone = posix_tz.get_posix_tz(settings.TIME_ZONE)
        if not system.timezone:
            system.timezone = 'UTC'

    # Reboot system in 3 seconds after a kernel panic.
    cfg.sysctl.set_variable('kernel.panic', 3)


@cgm_base.register_platform_module('openwrt', 11)
def user_accounts(node, cfg):
    """
    Configures password authentication for root user account.
    """

    cfg.accounts.add_user('nobody', '*', 65534, 65534, '/var', '/bin/false')

    try:
        auth = node.config.core.authentication(onlyclass=cgm_models.PasswordAuthenticationConfig).get()
        cfg.accounts.add_user('root', auth.password, 0, 0, '/tmp', '/bin/ash')
    except cgm_models.AuthenticationConfig.MultipleObjectsReturned:
        raise cgm_base.ValidationError(_("Multiple root passwords are not supported!"))
    except cgm_models.AuthenticationConfig.DoesNotExist:
        # If there is no password authentication, we still need to create a default root account
        # as otherwise authentication will not be possible. In this case, we use a random password.
        cfg.accounts.add_user('root', crypto.get_random_string(), 0, 0, '/tmp', '/bin/ash')


@cgm_base.register_platform_module('openwrt', 15)
def usb(node, cfg):
    """
    Install USB modules for devices which support it.
    """

    device = node.config.core.general().get_device()
    if not device:
        return

    if device.usb:
        # Include base USB packages for devices supporting USB.
        # TODO: Perhaps this should be made device-specific so only the needed packages are installed.
        cfg.packages.update([
            'kmod-usb2',
            'kmod-usb-ohci',
            'kmod-usb-uhci',
        ])

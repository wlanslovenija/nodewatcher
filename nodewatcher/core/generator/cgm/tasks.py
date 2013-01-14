from celery.task import task as celery_task

from nodewatcher.core.registry import loader
from nodewatcher.core.generator.cgm import base as cgm_base
from . import signals

@celery_task()
def background_build(node, platform, cfg):
    """
    A task for deferred formatting of node configuration and building of
    a firmware image.

    :param node: Node instance
    :parma platform: Platform name
    :param cfg: Generated configuration (platform-dependent)
    """

    # Ensure that all CGMs are loaded before doing processing
    loader.load_modules("cgm")
    platform = cgm_base.get_platform(platform)

    # Dispatch pre-build signal
    signals.pre_firmware_build.send(sender = None, node = node, platform = platform, cfg = cfg)

    # Build the firmware and obtain firmware files
    try:
        files = platform.build(node, cfg)
    except cgm_base.BuildError:
        # Dispatch error signal
        signals.fail_firmware_build.send(sender = None, node = node, platform = platform, cfg = cfg)
        return

    # Dispatch signal that can be used to modify files
    signals.process_firmware_files.send(sender = None, node = node, platform = platform, cfg = cfg, files = files)

    # TODO: Move firmware files to proper location

    # Dispatch signal that can be used to notify users
    signals.post_firmware_build.send(sender = None, node = node, platform = platform, cfg = cfg, files = files)

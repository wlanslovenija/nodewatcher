import os

from celery.task import task as celery_task

from django.conf import settings
from django.core import files as django_files
from django.core.files import storage as django_storage

from ...registry import loader
from ...generator.cgm import base as cgm_base

from . import signals


@celery_task()
def background_build(node, platform, cfg):
    """
    A task for deferred formatting of node configuration and building of
    a firmware image.

    :param node: Node instance
    :param platform: Platform name
    :param cfg: Generated configuration (platform-dependent)
    """

    # Ensure that all CGMs are loaded before doing processing
    loader.load_modules("cgm")
    platform = cgm_base.get_platform(platform)

    # Dispatch pre-build signal
    signals.pre_firmware_build.send(sender=None, node=node, platform=platform, cfg=cfg)

    # Build the firmware and obtain firmware files
    try:
        files = platform.build(node, cfg)
    except cgm_base.BuildError:
        # Dispatch error signal
        signals.fail_firmware_build.send(sender=None, node=node, platform=platform, cfg=cfg)
        return

    # Copy firmware files to proper location
    storage = django_storage.get_storage_class(settings.GENERATOR_STORAGE)()
    fw_files = []
    for fw_name in files:
        with open(fw_name, 'r') as fw_file:
            fw_files.append(storage.save(os.path.basename(fw_name), django_files.File(fw_file)))

    # Dispatch signal that can be used to modify files
    signals.post_firmware_build.send(
        sender=None, node=node, platform=platform, cfg=cfg,
        files=fw_files,
        storage=storage
    )

    # Dispatch finalize signal
    signals.finalize_firmware_build.send(
        sender=None, node=node, platform=platform, cfg=cfg,
        files=fw_files,
        storage=storage
    )

from celery.task import task as celery_task

# TODO: This app probably needs models.py and to be added to INSTALLED_APPS for this task to be self-discovered
@celery_task()
def format_and_build(node, platform, cfg):
    """
    A task for deferred formatting of node configuration and building of
    a firmware image.

    :param node: Node instance
    :param cfg: Generated configuration (platform-dependent)
    """
    formatted_cfg = platform.format(cfg)
    firmware = platform.build(formatted_cfg)
    # TODO Execute notification hooks that the firmware is ready?

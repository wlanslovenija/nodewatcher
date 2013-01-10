from celery.task import task as celery_task

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
    # TODO: Execute notification hooks that the firmware is ready? Signals should be used.

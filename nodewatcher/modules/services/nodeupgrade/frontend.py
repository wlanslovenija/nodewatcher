from django.conf import settings

from nodewatcher.core.frontend import components
from nodewatcher.core.generator import models as generator_models


def filter_platform(platform):
    def visible(partial, request, context):
        # Only display instructions when nodeupgrade has been configured.
        if not getattr(settings, 'NODEUPGRADE_SERVER', None):
            return False

        # Only display instructions when build has successfully completed.
        if context['build'].status != generator_models.BuildResult.OK:
            return False

        # Only display instructions for the correct platform.
        if context['build'].builder.platform != platform:
            return False

        return True

    return visible

# OpenWrt nodeupgrade instructions.
components.partials.get_partial('generator_view_build_partial').add(components.PartialEntry(
    name='nodeupgrade_openwrt',
    weight=100,
    visible=filter_platform('openwrt'),
    template='nodeupgrade/build_result_openwrt.html',
))

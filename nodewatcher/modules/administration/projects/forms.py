from nodewatcher.utils import hookable
from nodewatcher.core.allocation.ip import forms as ip_forms
from . import models

class ProjectIpAddressAllocatorMixin(hookable.HookHandler):
    """
    Project-based pool selection.
    """

    def filter_pools(self, item, cfg, request):
        try:
            # Only list the pools that are available for the selected project
            self.fields['pool'].queryset = self.fields['pool'].queryset.filter(
                projects = cfg['core.project'][0].project
            )
        except (models.Project.DoesNotExist, KeyError, AttributeError):
            pass

ip_forms.IpAddressAllocatorFormMixin.register_hooks(ProjectIpAddressAllocatorMixin)

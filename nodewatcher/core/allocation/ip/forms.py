from django.db.models import fields
from django.utils.translation import ugettext as _

from . import models as pool_models
from ...registry import fields as registry_fields

# TODO: Project model should be moved to core
from nodewatcher.legacy.nodes import models as nodes_models

class IpAddressAllocatorFormMixin(object):
    """
    A mixin for address allocator forms.
    """
    def modify_to_context(self, item, cfg, request):
        """
        Dynamically modifies the form.
        """
        # Only display pools that are available to the selected project
        qs = self.fields['pool'].queryset
        try:
            qs = qs.filter(projects = cfg['core.project'][0].project)
            qs = qs.filter(family = item.family)
            qs = qs.order_by("description", "ip_subnet")
        except (nodes_models.Project.DoesNotExist, KeyError, AttributeError):
            qs = qs.none()

        self.fields['pool'].queryset = qs

        # Only display prefix length range that is available for the selected pool
        try:
            pool = item.pool
            self.fields['prefix_length'] = registry_fields.SelectorFormField(
                label = _("Prefix Length"),
                choices = fields.BLANK_CHOICE_DASH + [
                (plen, "/%s" % plen)
                for plen in xrange(pool.prefix_length_minimum, pool.prefix_length_maximum + 1)
                ],
                initial = pool.prefix_length_default,
                coerce = int,
                empty_value = None
            )
        except (pool_models.IpPool.DoesNotExist, AttributeError):
            self.fields['prefix_length'] = registry_fields.SelectorFormField(label = _("Prefix Length"), choices = fields.BLANK_CHOICE_DASH)

        # If user has sufficient permissions, enable manual entry
        try:
            if not request.user.has_perm('can_allocate_manually', item.pool):
                del self.fields['subnet_hint']
        except pool_models.IpPool.DoesNotExist:
            del self.fields['subnet_hint']

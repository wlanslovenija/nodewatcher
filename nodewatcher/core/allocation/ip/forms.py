from django.db.models import fields
from django.utils.translation import ugettext as _

from ...registry import fields as registry_fields

from . import models as pool_models, signals


class IpAddressAllocatorFormMixin(object):
    """
    A mixin for address allocator forms.
    """

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically modifies the form.
        """

        # Only display pools that are available
        qs = self.fields['pool'].queryset
        qs = qs.filter(family=item.family)
        qs = qs.order_by('description', 'ip_subnet')
        self.fields['pool'].queryset = qs

        # Enable other modules to further filter the pools per some other attributes
        signals.filter_pools.send(
            sender=self, pool=self.fields['pool'], item=item,
            cfg=cfg, request=request
        )

        # Only display prefix length range that is available for the selected pool
        try:
            pool = item.pool
            self.fields['prefix_length'] = registry_fields.SelectorFormField(
                label=_("Prefix Length"),
                choices=fields.BLANK_CHOICE_DASH + [
                    (plen, '/%s' % plen) for plen in xrange(pool.prefix_length_minimum, pool.prefix_length_maximum + 1)
                ],
                initial=pool.prefix_length_default,
                coerce=int,
                empty_value=None,
            )
        except (pool_models.IpPool.DoesNotExist, AttributeError):
            self.fields['prefix_length'] = registry_fields.SelectorFormField(label=_("Prefix Length"), choices=fields.BLANK_CHOICE_DASH)

        # If user has sufficient permissions, enable manual entry
        try:
            if not request.user.has_perm('can_allocate_manually', item.pool):
                del self.fields['subnet_hint']
        except pool_models.IpPool.DoesNotExist:
            del self.fields['subnet_hint']

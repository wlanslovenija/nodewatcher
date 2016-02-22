from django.contrib import admin

from guardian import admin as guardian_admin

from . import models


class IpPoolAdmin(guardian_admin.GuardedModelAdmin):
    ordering = ('description',)

    def get_queryset(self, request):
        qs = super(IpPoolAdmin, self).get_queryset(request)
        # Hide non-top-level pools.
        qs = qs.filter(parent=None)

        return qs

admin.site.register(models.IpPool, IpPoolAdmin)

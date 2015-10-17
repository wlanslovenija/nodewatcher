from django.contrib import admin

from . import models


class IpPoolAdmin(admin.ModelAdmin):
    ordering = ('description',)

    def get_queryset(self, request):
        qs = super(IpPoolAdmin, self).get_queryset(request)
        # Hide non-top-level pools.
        qs = qs.filter(parent=None)

        return qs

admin.site.register(models.IpPool, IpPoolAdmin)

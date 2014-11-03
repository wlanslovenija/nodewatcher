from django.contrib import admin

from . import models


class IpPoolAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.IpPool, IpPoolAdmin)

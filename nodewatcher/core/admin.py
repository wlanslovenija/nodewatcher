from django.contrib import admin

from guardian import admin as guardian_admin

from . import models


class NodeAdmin(guardian_admin.GuardedModelAdmin):
    readonly_fields = ('uuid',)

admin.site.register(models.Node, NodeAdmin)

from django.contrib import admin

from . import models


class BuildChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'last_modified', 'default')
    list_filter = ('default',)


class BuildVersionAdmin(admin.ModelAdmin):
    pass


class BuilderAdmin(admin.ModelAdmin):
    list_display = ('host', 'platform', 'architecture', 'version')
    list_filter = ('platform', 'architecture', 'version')

admin.site.register(models.BuildChannel, BuildChannelAdmin)
admin.site.register(models.BuildVersion, BuildVersionAdmin)
admin.site.register(models.Builder, BuilderAdmin)

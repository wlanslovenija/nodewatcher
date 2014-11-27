from django.contrib import admin

from . import models


class GlobalAuthenticationKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'fingerprint', 'created', 'enabled')

admin.site.register(models.GlobalAuthenticationKey, GlobalAuthenticationKeyAdmin)

from django.contrib import admin
from django.contrib.auth import admin as auth_admin, models as auth_models

from . import forms, models


class UserProfileAndSettingsInline(admin.StackedInline):
    model = models.UserProfileAndSettings
    can_delete = False
    verbose_name = 'profile'
    verbose_name_plural = 'profile'
    fieldsets = models.UserProfileAndSettings.fieldsets
    view_on_site = False


# Define a new User admin.
class UserAdmin(auth_admin.UserAdmin):
    inlines = (UserProfileAndSettingsInline,)
    form = forms.AdminUserChangeForm
    add_form = forms.AdminUserCreationForm
    add_fieldsets = forms.user_add_fieldsets


# Re-register UserAdmin.
admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdmin)

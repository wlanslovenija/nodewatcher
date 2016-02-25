from django.core import urlresolvers
from django.contrib import admin
from django.contrib.auth import admin as auth_admin, models as auth_models
from django.utils import html
from django.utils.translation import ugettext_lazy as _

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
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'staff', 'superuser', 'groups_column')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    empty_value_display = _("None")

    # Making column label shorter.
    def superuser(self, user):
        return user.is_superuser
    superuser.short_description = _("Superuser")
    superuser.boolean = True
    superuser.admin_order_field = 'is_superuser'

    # Making column label shorter.
    def staff(self, user):
        return user.is_staff
    staff.short_description = _("Staff")
    staff.boolean = True
    staff.admin_order_field = 'is_staff'

    def groups_column(self, user):
        return html.format_html_join(', ', '<a href="{}">{}</a>', (
            (urlresolvers.reverse('admin:auth_group_change', args=(group.pk,)), group.name) for group in user.groups.all().only('name')
        ))
    groups_column.short_description = _("Groups")

    def get_queryset(self, request):
        # Optimization to prefetch all groups because we are displaying them for all users.
        return super(UserAdmin, self).get_queryset(request).prefetch_related('groups')

# Re-register UserAdmin.
admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdmin)

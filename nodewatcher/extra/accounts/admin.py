from django.core import urlresolvers
from django.contrib import admin
from django.contrib.auth import admin as auth_admin, models as auth_models
from django.utils import html
from django.utils.translation import ugettext_lazy as _

from guardian import core as guardian_core, shortcuts, utils as guardian_utils

from nodewatcher.core import models as core_models
from nodewatcher.utils import permissions

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

    class Media:
        css = {
            'all': ('admin/auth/user/change_form.css',),
        }

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

    def groups_links(self, groups):
        return html.format_html_join(', ', '<a href="{}">{}</a>', (
            (urlresolvers.reverse('admin:auth_group_change', args=(group.pk,)), group.name) for group in groups.only('name')
        ))

    def groups_column(self, user):
        return self.groups_links(user.groups.all())
    groups_column.short_description = _("Groups")

    def get_queryset(self, request):
        # Optimization to prefetch all groups because we are displaying them for all users.
        return super(UserAdmin, self).get_queryset(request).prefetch_related('groups')

    def get_nodes_entry(self, user, node):
        return {
            'node': node,
            'user_permissions': shortcuts.get_user_perms(user, node),
            'group_permissions': shortcuts.get_group_perms(user, node),
            'groups': self.groups_links(shortcuts.get_groups_with_perms(node).filter(user=user)),
        }

    def get_nodes(self, object_id):
        user = auth_models.User.objects.get(pk=object_id)
        return (self.get_nodes_entry(user, node) for node in permissions.get_objects_for_user(user, [], core_models.Node, use_superusers=False))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['nodes'] = self.get_nodes(object_id)
        return super(UserAdmin, self).change_view(request, object_id, form_url, extra_context)

# Re-register UserAdmin.
admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdmin)

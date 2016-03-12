from django import forms as django_forms
from django.core import urlresolvers
from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.auth import admin as auth_admin, models as auth_models
from django.db.models.fields import reverse_related
from django.utils import html, translation
from django.utils.translation import ugettext_lazy as _

from guardian import shortcuts

from nodewatcher.core import models as core_models

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
            'all': ('admin/auth/change_form.css',),
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
        return (self.get_nodes_entry(user, node) for node in shortcuts.get_objects_for_user(user, [], core_models.Node, with_superuser=False, accept_global_perms=False))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['nodes'] = self.get_nodes(object_id)
        return super(UserAdmin, self).change_view(request, object_id, form_url, extra_context)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'user_permissions':
            db_field.help_text = _("Specific global permissions for this user. A user will get permissions over all instances of a permission's model.")

        return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


# TODO: Needed until this ticket is resolved; https://code.djangoproject.com/ticket/897
class GroupAdminForm(django_forms.ModelForm):
    users = django_forms.ModelMultipleChoiceField(
        queryset=auth_admin.User.objects.all(),
        required=False,
        widget=widgets.FilteredSelectMultiple(
            verbose_name=_("users"),
            is_stacked=False,
        ),
        help_text=translation.string_concat(
            _("Members of this group."),
            " ",
            _("Hold down \"Control\", or \"Command\" on a Mac, to select more than one."),
        )
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save(self, commit=True):
        group = super(GroupAdminForm, self).save(commit=commit)

        if commit:
            # This immediately changes the database and there is no need to call save again.
            group.user_set = self.cleaned_data['users']
        else:
            old_save_m2m = self.save_m2m
            def new_save_m2m():
                old_save_m2m()
                # This immediately changes the database and there is no need to call save again.
                group.user_set = self.cleaned_data['users']
            self.save_m2m = new_save_m2m

        return group


# Define a new Group admin.
class GroupAdmin(auth_admin.GroupAdmin):
    form = GroupAdminForm

    class Media:
        css = {
            'all': ('admin/auth/change_form.css',),
        }

    def get_nodes_entry(self, group, node):
        return {
            'node': node,
            'permissions': shortcuts.get_group_perms(group, node),
        }

    def get_nodes(self, object_id):
        group = auth_models.Group.objects.get(pk=object_id)
        return (self.get_nodes_entry(group, node) for node in shortcuts.get_objects_for_group(group, [], core_models.Node, accept_global_perms=False))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['nodes'] = self.get_nodes(object_id)
        return super(GroupAdmin, self).change_view(request, object_id, form_url, extra_context)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'permissions':
            db_field.help_text = _("Global permissions for this group. All users in the group will get permissions over all instances of a permission's model.")

        return super(GroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(GroupAdmin, self).get_form(request, obj, **kwargs)

        # Invert the user_set.rel ManyToManyRel.
        remote_field = reverse_related.ManyToManyRel(
            self.model.user_set.rel.get_related_field(), self.model.user_set.rel.related_model,
            symmetrical=self.model.user_set.rel.symmetrical,
            through=self.model.user_set.rel.through,
            db_constraint=self.model.user_set.rel.db_constraint,
        )

        # We have to wrap it only because otherwise the field help text is moved
        # by JavaScript above the field and is not kept below.
        form.base_fields['users'].widget = widgets.RelatedFieldWidgetWrapper(
            form.base_fields['users'].widget, remote_field, self.admin_site,
            # To simplify the interface, we do not allow adding users from this view.
            can_add_related=False,
            can_change_related=False,
            can_delete_related=False,
        )

        return form

# Re-register UserAdmin and GroupAdmin.
admin.site.unregister(auth_models.User)
admin.site.register(auth_models.User, UserAdmin)
admin.site.unregister(auth_models.Group)
admin.site.register(auth_models.Group, GroupAdmin)

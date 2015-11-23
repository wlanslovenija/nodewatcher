from django.conf import settings
from django.core import validators as core_validators
from django.forms import forms, models as forms_models
from django.contrib.admin import util as admin_util
from django.contrib import auth
from django.contrib.auth import admin as auth_admin, forms as auth_forms, models as auth_models
from django.utils.translation import ugettext_lazy as _

from . import metaforms, models, validators

# Fieldsets of fields we use both in admin and registration for the user object creation.
user_add_fieldsets = list(auth_admin.UserAdmin.add_fieldsets)
# UserAdmin.fieldsets[1] contains first name, last name and e-mail address.
user_add_fieldsets.append(auth_admin.UserAdmin.fieldsets[1])

# Fieldsets of fields we use in registration for the user object modification.
# UserAdmin.fieldsets[1] contains first name, last name and e-mail address.
user_change_fieldsets = [auth_admin.UserAdmin.fieldsets[1]]


def alter_user_form_fields(form):
    """
    This function marks first name, last name and e-mail address fields as required in the given form. It validates
    hostname existence of the e-mail address and sets minimal length on the username field. It also adds some help texts
    to fields.
    """

    if 'username' in form.fields:
        # Minimal length (it is otherwise checked in a form field so we also check it just there).
        if not filter(lambda v: isinstance(v, core_validators.MinLengthValidator), form.fields['username'].validators):
            # We do not blindly append as field objects can be reused.
            form.fields['username'].validators.append(core_validators.MinLengthValidator(4))
        # We set it every time to be sure.
        form.fields['username'].min_length = 4
        form.fields['username'].help_text = _("Letters, digits and @/./+/-/_ only. Will be public.")

    # E-mail domain validation (we check it in a model field).
    emailfield = filter(lambda x: x.name == 'email', form.Meta.model._meta.fields)[0]
    # We replace core validator with our own extended version which also checks hostname existence.
    emailfield.validators = filter(lambda x: not isinstance(x, core_validators.EmailValidator), emailfield.validators)
    # We do not blindly append as field objects can be reused.
    if validators.validate_email_with_hostname not in emailfield.validators:
        emailfield.validators.append(validators.validate_email_with_hostname)

    # We add in a form field as it is too late to add in model field.
    form.fields['email'].help_text = _("Carefully enter your e-mail address as it will be used for account activation. It will be visible to other registered users.")
    form.fields['first_name'].help_text = _("By default used for attribution. You can hide it to be visible only to network administrators in privacy section bellow.")
    form.fields['last_name'].help_text = form.fields['first_name'].help_text

    # We want those fields to be required (`UserCreationForm.Meta.fields` is made from `user_add_fieldsets`).
    # `user_add_fieldsets` defines which fields we want at user creation.
    for field in AdminUserCreationForm.Meta.fields:
        # We check so that function works also on the user change form.
        if field in form.fields:
            form.fields[field].required = True


def check_password_length(form):
    """
    This function sets minimal length on the password field in the given form.
    """

    fieldname1 = 'new_password1' if 'new_password1' in form.fields else 'password1'
    fieldname2 = 'new_password2' if 'new_password2' in form.fields else 'password2'

    # Minimal length (it can be checked only in a form field).
    if not filter(lambda v: isinstance(v, core_validators.MinLengthValidator), form.fields[fieldname1].validators):
        # We do not blindly append as field objects can be reused.
        form.fields[fieldname1].validators.append(core_validators.MinLengthValidator(6))
    # We set it every time to be sure.
    form.fields[fieldname1].min_length = 6
    form.fields[fieldname1].help_text = _("Minimal password length is 6.")
    form.fields[fieldname2].help_text = _("Enter the same password as above, for verification.")


class ValidateUsernameMixin(object):
    def clean_username(self):
        # Check for username existence in a case-insensitive manner.

        UserModel = auth.get_user_model()
        username = self.cleaned_data.get('username', None)
        if username is None:
            username = self.cleaned_data.get(UserModel.USERNAME_FIELD)

        # There was no change to the usernaem made.
        if self.instance and self.instance.username == username:
            return username

        # Username was changed, check if it maybe already exists.
        if UserModel._default_manager.filter(**{('%s__iexact' % UserModel.USERNAME_FIELD): username}).exists():
            raise forms.ValidationError(_("A user with that username already exists."))

        return username


class AdminUserCreationForm(ValidateUsernameMixin, auth_forms.UserCreationForm):
    """
    This class defines creation form for `django.contrib.auth.models.User` objects for admin interface.

    It adds first name, last name and e-mail address fields and marks them as required. It validates hostname part
    of the e-mail address and sets minimal length on username and password fields.
    """

    # Admin interface does not use our form-level `fieldsets`.

    class Meta(auth_forms.UserCreationForm.Meta):
        # Both admin and registration user object creation forms share the same fields.
        fields = admin_util.flatten_fieldsets(user_add_fieldsets)

    def __init__(self, *args, **kwargs):
        super(AdminUserCreationForm, self).__init__(*args, **kwargs)

        alter_user_form_fields(self)
        check_password_length(self)


class UserCreationForm(AdminUserCreationForm):
    """
    This class defines creation form for `django.contrib.auth.models.User` objects.
    """

    error_css_class = 'error'
    required_css_class = 'required'
    fieldsets = user_add_fieldsets


class AdminUserChangeForm(ValidateUsernameMixin, auth_forms.UserChangeForm):
    """
    This class defines change form for `django.contrib.auth.models.User` objects for admin interface.

    It marks first name, last name and e-mail address fields as required. It validates hostname part of the e-mail
    address and sets minimal length on the username field.
    """

    # For user object modification we leave things as they are for admin.

    def __init__(self, *args, **kwargs):
        super(AdminUserChangeForm, self).__init__(*args, **kwargs)

        # Making sure we use the same validation on all forms.
        alter_user_form_fields(self)


class UserChangeForm(AdminUserChangeForm):
    """
    This class defines change form for `django.contrib.auth.models.User` objects with fields limited only to first name,
    last name and e-mail address.
    """

    error_css_class = 'error'
    required_css_class = 'required'
    fieldsets = user_change_fieldsets

    # Removing parent field.
    password = None

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

        self.fields['email'].help_text = _("If you change your e-mail address you will have to activate your account again so carefully enter it. It will be visible to other registered users.")

    class Meta(AdminUserChangeForm.Meta):
        # For registration user modification we use our set of fields.
        fields = admin_util.flatten_fieldsets(user_change_fieldsets)


class UserProfileAndSettingsChangeForm(forms_models.ModelForm):
    """
    This class defines change form for `nodewatcher.extra.accounts.models.UserProfileAndSettings` objects.
    """

    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = models.UserProfileAndSettings
        fields = forms_models.ALL_FIELDS


class AccountRegistrationForm(metaforms.FieldsetsFormMixin, metaforms.ParentsIncludedModelFormMixin, UserCreationForm, UserProfileAndSettingsChangeForm):
    """
    This class defines combined form for `django.contrib.auth.models.User` and `nodewatcher.extra.accounts.models.UserProfileAndSettings` objects.
    It is used for user registration.
    """

    error_css_class = 'error'
    required_css_class = 'required'
    fieldsets = UserCreationForm.fieldsets + list(UserProfileAndSettingsChangeForm.Meta.model.fieldsets)

    def save(self, commit=True):
        user, profile = super(AccountRegistrationForm, self).save(False)

        # We ignore `commit` argument because we have to save `user` to be able to set `profile`'s reference.
        user.save()
        profile.user = user
        profile.save()

        return user

    __metaclass__ = metaforms.ParentsIncludedModelFormMetaclass


class AuthenticationForm(auth_forms.AuthenticationForm):
    """
    This class adds CSS classes to `django.contrib.auth.forms.AuthenticationForm` form.
    """

    error_css_class = 'error'
    required_css_class = 'required'
    error_messages = dict(auth_forms.AuthenticationForm.error_messages, invalid_login=_("Please enter a correct username and password. Note that password is case-sensitive."))


class PasswordResetForm(auth_forms.PasswordResetForm):
    """
    This class adds CSS classes to `django.contrib.auth.forms.PasswordResetForm` form.
    """

    error_css_class = 'error'
    required_css_class = 'required'

    def save(self, **kwargs):
        # We are trying to use setting everywhere and not `request.is_secure()`.
        kwargs['use_https'] = getattr(settings, 'USE_HTTPS', False)

        return super(PasswordResetForm, self).save(**kwargs)


class SetPasswordForm(auth_forms.SetPasswordForm):
    """
    This class adds CSS classes to `django.contrib.auth.forms.SetPasswordForm` form.
    It sets minimal length and help text on password field.
    """

    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)

        check_password_length(self)


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    """
    This class adds CSS classes to `django.contrib.auth.forms.PasswordChangeForm` form.
    It sets minimal length and help text on password field.
    """

    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        check_password_length(self)

# TODO: Probably not needed anymore in Django 1.9.
#       See: https://github.com/django/django/commit/28986da4ca167ae257abcaf7caea230eca2bcd80
PasswordChangeForm.base_fields = auth_forms.PasswordChangeForm.base_fields


class AccountChangeForm(metaforms.FieldsetsFormMixin, metaforms.ParentsIncludedModelFormMixin, UserChangeForm, UserProfileAndSettingsChangeForm):
    """
    This class defines combined change form for `django.contrib.auth.models.User` and `nodewatcher.extra.accounts.models.UserProfileAndSettings` objects.
    """

    error_css_class = 'error'
    required_css_class = 'required'
    fieldsets = UserChangeForm.fieldsets + list(UserProfileAndSettingsChangeForm.Meta.model.fieldsets)

    __metaclass__ = metaforms.ParentsIncludedModelFormMetaclass

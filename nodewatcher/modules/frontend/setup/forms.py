from django import forms
from django.core import validators as core_validators
from django.contrib.auth import forms as auth_forms, models as auth_models
from django.utils.translation import ugettext_lazy as _

from guardian import utils as guardian_utils

from . import validators


def alter_creation_form(form):
    """
    This function marks e-mail address field as required in the given form. It validates
    hostname existence of the e-mail address and sets minimal length on the username field.
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


class AdminCreationForm(auth_forms.UserCreationForm):
    class Meta(auth_forms.UserCreationForm.Meta):
        fields = auth_forms.UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super(AdminCreationForm, self).__init__(*args, **kwargs)

        alter_creation_form(self)
        check_password_length(self)

        self.fields['email'].help_text = _("Carefully enter your e-mail address. It will be visible to other registered users.")
        self.fields['email'].required = True

    def clean(self):
        cleaned_data = super(AdminCreationForm, self).clean()

        if auth_models.User.objects.exclude(pk=guardian_utils.get_anonymous_user().pk).exists():
            raise forms.ValidationError(_("Only the initial admin account can be created."))

        return cleaned_data

    def save(self, commit=True):
        user = super(AdminCreationForm, self).save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

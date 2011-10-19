import datetime

from django.core import validators as core_validators
from django.forms import forms
from django.forms import models as forms_models
from django.forms.extras import widgets
from django.contrib.admin import util as admin_util
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import models as auth_models
from django.utils import text as utils_text
from django.utils.translation import ugettext_lazy as _

from web.account import metaforms
from web.account import models
from web.account import validators

user_add_fieldsets = list(auth_admin.UserAdmin.add_fieldsets)
user_add_fieldsets.append(auth_admin.UserAdmin.fieldsets[1]) # UserAdmin.fieldsets[1] contains first name, last name and e-mail address

user_change_fieldsets = [auth_admin.UserAdmin.fieldsets[1]] # UserAdmin.fieldsets[1] contains first name, last name and e-mail address

def alter_user_form_fields(form):
  """
  This function marks first name, last name and e-mail address fields as required in the given form. It validates
  hostname existence of the e-mail address and sets minimal length on the username field. It also adds some help texts
  to fields.
  """
    
  # Minimal length (it is otherwise checked in a form field so we also check it just there)
  if not filter(lambda v: isinstance(v, core_validators.MinLengthValidator), form.fields['username'].validators):
    # We do not blindly append as field objects can be reused
    form.fields['username'].validators.append(core_validators.MinLengthValidator(4))
  # We set it every time to be sure
  form.fields['username'].min_length = 4
  
  # E-mail domain validation (we check it in a model field)
  emailfield = filter(lambda x: x.name == 'email', form.Meta.model._meta.fields)[0]
  # We replace core validator with our own extended version which also checks hostname existence
  emailfield.validators = filter(lambda x: not isinstance(x, core_validators.EmailValidator), emailfield.validators)
  if validators.validate_email_with_hostname not in emailfield.validators:
    # We do not blindly append as field objects can be reused
    emailfield.validators.append(validators.validate_email_with_hostname)
  
  # We add in a form field as it is too late to add in model field
  form.fields['email'].help_text = _('Carefully enter your e-mail address as it will be used for account activation. It will be visible to other registered users.')
  form.fields['first_name'].help_text = _('It will be visible only to network administrators.')
  form.fields['last_name'].help_text = form.fields['first_name'].help_text
  
  # We want those fields to be required (UserCreationForm.Meta.fields is made from user_add_fieldsets)
  # user_add_fieldsets defines which fields we want at user creation
  for field in UserCreationForm.Meta.fields:
    # We check so that function works also on the user change form
    if field in form.fields:
      form.fields[field].required = True

def check_password_length(form):
  """
  This function sets minimal length on the password field in the given form.
  """
  
  fieldname1 = 'new_password1' if 'new_password1' in form.fields else 'password1'
  fieldname2 = 'new_password2' if 'new_password2' in form.fields else 'password2'
  
  # Minimal length (it can be checked only in a form field)
  if not filter(lambda v: isinstance(v, core_validators.MinLengthValidator), form.fields[fieldname1].validators):
    # We do not blindly append as field objects can be reused
    form.fields[fieldname1].validators.append(core_validators.MinLengthValidator(6))
  # We set it every time to be sure
  form.fields[fieldname1].min_length = 6
  form.fields[fieldname1].help_text = _('Minimal password length is 6.')
  form.fields[fieldname2].help_text = _('Enter the same password as above, for verification.')

class UserCreationForm(auth_forms.UserCreationForm):
  """
  This class defines creation form for `django.contrib.auth.models.User` objects.
  
  It adds first name, last name and e-mail address fields and marks them as required. It validates hostname part of the e-mail
  address and sets minimal length on username and password fields.
  """
  
  error_css_class = 'error'
  required_css_class = 'required'
  fieldset = user_add_fieldsets

  class Meta(auth_forms.UserCreationForm.Meta):
    # By default first name, last name and e-mail address are not created at user creation, but we want them
    # user_add_fieldsets defines which fields we want at user creation
    fields = list(auth_forms.UserCreationForm.Meta.fields)
    for fieldset in user_add_fieldsets:
      fields.extend(fieldset[1]['fields'])
    
  def __init__(self, *args, **kwargs):
    super(UserCreationForm, self).__init__(*args, **kwargs)
    alter_user_form_fields(self)
    check_password_length(self)

  def clean_password2(self):
    # If password1 is invalid (and thus missing) we do not check password2 and let user first correct password1 error
    # There is a ticket about this: http://code.djangoproject.com/ticket/7833#comment:6
    if not self.cleaned_data.get('password1'):
      return self.cleaned_data.get('password2')
    return super(UserCreationForm, self).clean_password2()

  def clean_username(self):
    # Check for username existence in a case-insensitive manner
    username = super(UserCreationForm, self).clean_username()
    try:
      auth_models.User.objects.get(username__iexact=username)
    except auth_models.User.DoesNotExist:
      return username
    raise forms.ValidationError(_("A user with that username already exists."))

class AdminUserChangeForm(auth_forms.UserChangeForm):
  """
  This class defines change form for `django.contrib.auth.models.User` objects for admin inteface.
  
  It marks first name, last name and e-mail address fields as required. It validates hostname part of the e-mail
  address and sets minimal length on the username field.
  """
  
  error_css_class = 'error'
  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    super(AdminUserChangeForm, self).__init__(*args, **kwargs)
    alter_user_form_fields(self)

class UserChangeForm(AdminUserChangeForm):
  """
  This class defines change form for `django.contrib.auth.models.User` objects with fields limited only to first name,
  last name and e-mail address.
  """
    
  error_css_class = 'error'
  required_css_class = 'required'
  fieldset = user_change_fieldsets
  
  def __init__(self, *args, **kwargs):
    # This is here just because of the bug in Django which does not remove explicitly declared fields in parent class from
    # a subclass form when field is not declared in Meta.fields or even if it is defined in Meta.exclude
    # So we remove such field (in this case username field) here ourselves
    super(UserChangeForm, self).__init__(*args, **kwargs)
    del self.fields['username']
    
    self.fields['email'].help_text = _('If you change your e-mail address you will have to activate your account again so carefully enter it. It will be visible to other registered users.')
  
  class Meta(AdminUserChangeForm.Meta):
    fields = admin_util.flatten_fieldsets(user_change_fieldsets)

class UserProfileAndSettingsChangeForm(forms_models.ModelForm):
  """
  This class defines change form for `web.account.models.UserProfileAndSettings` objects.
  """

  error_css_class = 'error'
  required_css_class = 'required'

  class Meta:
    model = models.UserProfileAndSettings

class AccountRegistrationForm(metaforms.FieldsetFormMixin, metaforms.ParentsIncludedModelFormMixin, UserCreationForm, UserProfileAndSettingsChangeForm):
  """
  This class defines combined form for `django.contrib.auth.models.User` and `web.account.models.UserProfileAndSettings` objects.
  It is used for user registration.
  """
  
  error_css_class = 'error'
  required_css_class = 'required'
  fieldset = UserCreationForm.fieldset + list(UserProfileAndSettingsChangeForm.Meta.model.fieldset)
  
  def save(self, commit=True):
    # We disable save method as registration module (through `web.account.regbackend.ProfileBackend` backend) takes
    # care of user and user profile objects creation and we do not use it for changing data
    assert False
    return None
  
  __metaclass__ = metaforms.ParentsIncludedModelFormMetaclass

class AuthenticationForm(auth_forms.AuthenticationForm):
  """
  This class adds CSS classes to `django.contrib.auth.forms.AuthenticationForm` form.
  """
  
  error_css_class = 'error'
  required_css_class = 'required'

class PasswordResetForm(auth_forms.PasswordResetForm):
  """
  This class adds CSS classes to `django.contrib.auth.forms.PasswordResetForm` form.
  """
  
  error_css_class = 'error'
  required_css_class = 'required'

class SetPasswordForm(auth_forms.SetPasswordForm):
  """
  This class adds CSS classes to `django.contrib.auth.forms.SetPasswordForm` form. It sets minimal length and help text
  on password field.
  """
  
  error_css_class = 'error'
  required_css_class = 'required'
  
  def __init__(self, *args, **kwargs):
    super(SetPasswordForm, self).__init__(*args, **kwargs)
    check_password_length(self)

class PasswordChangeForm(auth_forms.PasswordChangeForm):
  """
  This class adds CSS classes to `django.contrib.auth.forms.PasswordChangeForm` form. It sets minimal length and help text
  on password field.
  """
  
  error_css_class = 'error'
  required_css_class = 'required'
  
  def __init__(self, *args, **kwargs):
    super(PasswordChangeForm, self).__init__(*args, **kwargs)
    check_password_length(self)

class AccountChangeForm(metaforms.FieldsetFormMixin, metaforms.ParentsIncludedModelFormMixin, UserChangeForm, UserProfileAndSettingsChangeForm):
  """
  This class defines combined change form for `django.contrib.auth.models.User` and `web.account.models.UserProfileAndSettings` objects.
  """
  
  error_css_class = 'error'
  required_css_class = 'required'
  fieldset = UserChangeForm.fieldset + list(UserProfileAndSettingsChangeForm.Meta.model.fieldset)
  
  __metaclass__ = metaforms.ParentsIncludedModelFormMetaclass

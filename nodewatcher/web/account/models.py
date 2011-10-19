from django.conf import settings
from django.db import models as django_models
from django.contrib.auth import models as auth_models
from django.core import urlresolvers
from django.template import loader
from django.utils.translation import ugettext_lazy as _

from registration import models as registration_models

from phonenumber_field import modelfields as phonenumber_fields

from web.account import geo_fields
from web.account import utils
from web.nodes import models

class UserProfileAndSettings(django_models.Model):
  """
  This class represents an user profile and settings.
  """

  user = django_models.OneToOneField(auth_models.User, editable=False)

  phone_number = phonenumber_fields.PhoneNumberField(_('phone number'), help_text=_('Please enter your phone number in international format (e.g. +411234567) for use in emergency. It will be visible only to network administrators.'), null=True)
  country = geo_fields.CountryField(_('country'), blank=True, help_text=_('Where are you from? It will be public.'))
  language = geo_fields.LanguageField(_('language'), help_text=_('Choose the language you wish this site to be in.'))
  default_project = django_models.ForeignKey(models.Project, default=models.project_default, null=True, verbose_name=_('default project'))

  # AccountRegistrationForm and AccountChangeForm uses this
  fieldset = (
    (_('Additional personal info'), {
      'fields': ('phone_number', 'country'),
    }),
    (_('Settings'), {
      'fields': ('language', 'default_project'),
    }),
  )

  class Meta:
    verbose_name = _('user profile and settings')
    verbose_name_plural = _('users profiles and settings')

  def __unicode__(self):
    return u"profile and settings for %s" % (self.user)
  
  @django_models.permalink
  def get_absolute_url(self):
    return ('user_account',)

# Monkey patach registration_models.RegistrationProfile

def send_activation_email(instance, site, email_change=False):
  """
  Based on `registration.models.RegistrationProfile.send_activation_email` to extend activation e-mail template context with
  `email_change` boolean and other values.
  """

  protocol = 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'
  base_url = "%s://%s" % (protocol, site.domain)
  registration_activate_url = "%s%s" % (base_url, urlresolvers.reverse('registration_activate', args=(instance.activation_key,)))
  
  ctx_dict = {
    'activation_key': instance.activation_key,
    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
    'site': site,
    'base_url': base_url,
    'protocol': protocol,
    'network': {
      'name': settings.NETWORK_NAME,
      'home': settings.NETWORK_HOME,
      'contact': settings.NETWORK_CONTACT,
      'contact_page': settings.NETWORK_CONTACT_PAGE,
      'description': getattr(settings, 'NETWORK_DESCRIPTION', None),
    },
    'email_change': email_change,
    'registration_activate_url': registration_activate_url,
  }
  subject = loader.render_to_string('registration/activation_email_subject.txt', ctx_dict)
  subject = ''.join(subject.splitlines())
  
  message = loader.render_to_string('registration/activation_email.txt', ctx_dict)
  
  instance.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
registration_models.RegistrationProfile.send_activation_email = send_activation_email

orig_activation_key_expired = registration_models.RegistrationProfile.activation_key_expired
def activation_key_expired(instance):
  """
  Determines whether this `RegistrationProfile`'s activation key has expired.
  
  For users which have already logged in activation key never expires (they have probably changed their e-mail address).
  Otherwise original `registration.models.RegistrationProfile.activation_key_expired` rules apply.
  """

  if instance.activation_key == instance.ACTIVATED:
    return True
  if instance.user.last_login != instance.user.date_joined:
    return False
  return orig_activation_key_expired(instance)
activation_key_expired.boolean = True
registration_models.RegistrationProfile.activation_key_expired = activation_key_expired

try:
# So that signals are registred early on
  import web.account.signals
except ImportError:
  # Probably circular imports
  pass

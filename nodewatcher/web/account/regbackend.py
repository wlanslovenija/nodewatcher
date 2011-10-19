from django import dispatch
from django.forms import models as forms_models

from registration.backends import default as backends_default
from registration import signals as registration_signals

from web.account import forms
from web.account import utils

user_profile_registered = dispatch.Signal(providing_args=["user", "profile", "request"])

class ProfileBackend(backends_default.DefaultBackend):
  """
  This class defines a registration backend with support for user profiles.
  
  It uses extended user creation form with fields for user profile data.
  
  It sends `web.account.regbackend.user_profile_registered` signal with `user`, `profile` and `request` arguments`
  after user profile object has been populated with registered data.
  
  It is an extension of `registration.backends.default.DefaultBackend` backend.
  """
  
  def register(self, request, **kwargs):
    """
    Register a new user account, which will initially be inactive.

    It also creates corresponding user profile.
    """
    
    user = super(ProfileBackend, self).register(request, **kwargs)
    profile, created = utils.get_profile_model().objects.get_or_create(user=user)
    
    # lambda-object to the rescue
    form = lambda: None
    form.cleaned_data = kwargs
    
    # First name, last name and e-mail address are stored in user object
    forms_models.construct_instance(form, user)
    user.save()
    
    # Other fields are stored in user profile object
    forms_models.construct_instance(form, profile)
    profile.save()
    
    user_profile_registered.send(sender=self.__class__, user=user, profile=profile, request=request)
    
    return user
  
  def get_form_class(self, request):
    """
    Returns the default form class used for user registration.
    
    It returns `web.account.forms.AccountRegistrationForm` form which contains fields for both user and user profile objects.
    """

    return utils.initial_accepts_request(request, forms.AccountRegistrationForm)

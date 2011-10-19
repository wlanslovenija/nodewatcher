from django import http
from django import shortcuts
from django import template
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.sites import models as sites_models
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.utils import copycompat as copy

from registration import models as registration_models

from web.account import decorators
from web.account import forms
from web.account import signals

def user(request, username):
  """
  This view displays a public page for a given user.
  """
  
  return shortcuts.render_to_response("users/user.html", {
    'username': username,
  }, context_instance=template.RequestContext(request))

@decorators.authenticated_required
def account(request):
  """
  View which displays `web.account.forms.AccountChangeForm` form for users to change their account.
  
  If the user changes her e-mail address her account is inactivated and she gets an activation e-mail.
  """
  
  assert request.user.is_authenticated()
  
  if request.method == 'POST':
    stored_user = copy.copy(request.user)
    form = forms.AccountChangeForm(request.POST, instance=[request.user, request.user.get_profile()])
    if form.is_valid():
      objs = form.save()
      messages.success(request, _("Your account has been successfully updated."), fail_silently=True)
      
      old_email = stored_user.email
      new_email = request.user.email
      
      if old_email == new_email:
        return shortcuts.redirect(objs[-1]) # The last element is user profile object
      else:
        site = sites_models.Site.objects.get_current() if sites_models.Site._meta.installed else sites_models.RequestSite(request)
        
        request.user.is_active = False
        request.user.save()
        
        registration_profile = registration_models.RegistrationProfile.objects.create_profile(request.user)
        registration_profile.send_activation_email(site, email_change=True)
        
        url = urlresolvers.reverse('email_change_complete')
        
        return logout_redirect(request, next_page=url)
    else:
      # Restore user request object as it is changed by form.is_valid
      request.user = stored_user
      if hasattr(request.user, '_profile_cache'):
        # Invalidates profile cache
        delattr(request.user, '_profile_cache')
  else:
    form = forms.AccountChangeForm(instance=[request.user, request.user.get_profile()])
  
  return shortcuts.render_to_response("users/account.html", {
    'form': form,
  }, context_instance=template.RequestContext(request))

def logout_redirect(request, *args, **kwargs):
  """
  Logs out the user and redirects her to the log-in page or elsewhere, as specified.
  
  A wrapper (which prefers redirects) around `django.contrib.auth.views.logout` view which sends a `web.account.signals.user_logout` signal on logout.
  """
  
  kwargs.setdefault('redirect_field_name', auth.REDIRECT_FIELD_NAME)
  # We prefer redirect but explicit None for next_page makes it behave as the official logout view
  kwargs.setdefault('next_page', request.REQUEST.get(kwargs.get('redirect_field_name')) or settings.LOGIN_URL)
  
  user = request.user
  res = auth_views.logout(request, *args, **kwargs)
  signals.user_logout.send(sender=logout_redirect, request=request, user=user)
  return res

@decorators.anonymous_required
def login(request, *args, **kwargs):
  """
  Displays the login form and handles the login action.
  
  A wrapper around `django.contrib.auth.views.login` view which sends a `web.acount.signals.user_login` signal on successful login.
  """
  
  assert request.user.is_anonymous()

  kwargs.setdefault('authentication_form', forms.AuthenticationForm)
  res = auth_views.login(request, *args, **kwargs)
  if request.user.is_authenticated():
    signals.user_login.send(sender=login, request=request, user=request.user)
  return res

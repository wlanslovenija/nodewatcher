try:
  from functools import wraps
except ImportError:
  from django.utils.functional import wraps # Python 2.4 fallback.

from django import http
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.utils import decorators
from django.utils import http as utils_http
from django.utils.translation import ugettext_lazy as _

def user_test_required(test_func, message_func=None, message_level_func=lambda u: messages.INFO, redirect_url_func=lambda u: None, redirect_field_name=auth.REDIRECT_FIELD_NAME, decorator_id=None):
  """
  Decorator for views that checks that the user passes the given test, redirecting if necessary (by default to the profile page).
  The test should be a callable that takes the user object and returns True if the user passes. It can use optional message
  argument to tell the user the reason why she has be redirected, which should also be a callable that takes the user object as
  an argument.

  It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
  one used.
  """

  if decorator_id is None:
    decorator_id = id(user_test_required)
  
  def decorator(view_func):
    def _wrapped_view(request, *args, **kwargs):
      if test_func(request.user):
        return view_func(request, *args, **kwargs)
      path = utils_http.urlquote(request.get_full_path())
      tup = (redirect_url_func(request.user) or settings.LOGIN_REDIRECT_URL), redirect_field_name, path
      if message_func:
        messages.add_message(request, message_level_func(request.user), message_func(request.user), fail_silently=True)
      return http.HttpResponseRedirect('%s?%s=%s' % tup)

    wrapped_view_func = wraps(view_func, assigned=decorators.available_attrs(view_func))(_wrapped_view)
    wrapped_view_func.decorators = []
    if hasattr(view_func, 'decorators'):
      wrapped_view_func.decorators += view_func.decorators
    wrapped_view_func.decorators.append(decorator_id)

    return wrapped_view_func

  return decorator

def authenticated_required(function=None, message_func=lambda u: _("You have to be logged in while accessing the previous page. Please login to continue."), message_level_func=lambda u: messages.ERROR, redirect_url_func=lambda u: settings.LOGIN_URL, redirect_field_name=auth.REDIRECT_FIELD_NAME):
  """
  Decorator for views that checks that the user is logged in, redirecting if necessary (by default to the log-in page).

  It gives the user a message with a reason for redirect.

  It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
  one used.
  """
  
  actual_decorator = user_test_required(
    lambda u: u.is_authenticated(),
    message_func=message_func,
    message_level_func=message_level_func,
    redirect_url_func=redirect_url_func,
    redirect_field_name=redirect_field_name,
    decorator_id=id(authenticated_required),
  )
  
  if function:
    return actual_decorator(function)
  return actual_decorator

def anonymous_required(function=None, message_func=lambda u: _("You should not be logged in while accessing the previous page."), message_level_func=lambda u: messages.ERROR, redirect_url_func=lambda u: settings.LOGIN_REDIRECT_URL, redirect_field_name=auth.REDIRECT_FIELD_NAME):
  """
  Decorator for views that checks whether the user is anonymous, redirecting if necessary (by default to the profile page).

  It gives the user a message with a reason for redirect.

  It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
  one used.
  """
  
  actual_decorator = user_test_required(
    lambda u: u.is_anonymous(),
    message_func=message_func,
    message_level_func=message_level_func,
    redirect_url_func=redirect_url_func,
    redirect_field_name=redirect_field_name,
    decorator_id=id(anonymous_required),
  )
  
  if function:
    return actual_decorator(function)
  return actual_decorator

def permission_required(perm, message_func=lambda u: _("You do not have necessary permission to access the previous page."), message_level_func=lambda u: messages.ERROR, redirect_url_func=lambda u: settings.LOGIN_REDIRECT_URL, redirect_field_name=auth.REDIRECT_FIELD_NAME):
  """
  Decorator for views that checks whether the user has a particular permission enabled, redirecting if necessary (by default
  to the profile page).

  It gives the user a message with a reason for redirect.

  It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
  one used.
  """
  
  return user_passes_test(lambda u: u.has_perm(perm), message_func=message_func, message_level_func=message_level_func, redirect_url_func=redirect_url_func, redirect_field_name=redirect_field_name, decorator_id=id(permission_required))

def authenticated_permission_required(perm, message_func=lambda u: _("You do not have necessary permission to access the previous page.") if u.is_authenticated() else _("You have to be logged in while accessing the previous page. Please login to continue."), message_level_func=lambda u: messages.ERROR, redirect_url_func=lambda u: settings.LOGIN_REDIRECT_URL if u.is_authenticated() else settings.LOGIN_URL, redirect_field_name=auth.REDIRECT_FIELD_NAME):
  """
  Decorator for views that checks whether the user has authenticated and has a particular permission enabled, redirecting as
  necessary: if not authenticated to the log-in page, otherwise to the profile page.

  It also gives the user a proper message with a reason for redirect.

  It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
  one used.
  """
  
  return user_passes_test(lambda u: u.is_authenticated() and u.has_perm(perm), message_func=message_func, message_level_func=message_level_func, redirect_url_func=redirect_url_func, redirect_field_name=redirect_field_name, decorator_id=id(authenticated_permission_required))

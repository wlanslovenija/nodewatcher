from django import template
from django.core.urlresolvers import resolve

from web.account import decorators

register = template.Library()

@register.filter
def anonymous_required(value):
  """
  Returns True if view for given URL path string requires anonymous access.
  """

  # We remove possible query and fragment strings
  value = value.partition('?')[0]
  value = value.partition('#')[0]
  try:
    view, args, kwargs = resolve(value)
  except:
    return False
  if not hasattr(view, 'decorators'):
    return False
  return id(decorators.anonymous_required) in view.decorators

@register.filter
def authenticated_required(value):
  """
  Returns True if view for given URL path string requires authenticated access.
  """

  # We remove possible query and fragment strings
  value = value.partition('?')[0]
  value = value.partition('#')[0]
  try:
    view, args, kwargs = resolve(value)
  except:
    return False
  if not hasattr(view, 'decorators'):
    return False
  return id(decorators.authenticated_required) in view.decorators or id(decorators.authenticated_permission_required) in view.decorators

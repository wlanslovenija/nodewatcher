try:
  from functools import wraps
except ImportError:
  from django.utils.functional import wraps # Python 2.4 fallback.

from django import http
from django import shortcuts
from django.utils import decorators
from django.core import urlresolvers

from web.nodes import models

def redirect_helper(view_func, node_obj, *args, **kwargs):
  """
  Small redirect helper to redirect properly to the given function with original arguments.
  """
  
  # We reverse by name as view_func can be wrapped in decorators later so it would not be found when reversed
  module = getattr(view_func, '__module__', None)
  name = getattr(view_func, '__name__', None)
  view_func_name = "%s.%s" % (module, name)
  # We update arguments based on how others were passed to view_func
  if kwargs:
    kwargs['node'] = node_obj.get_current_id()
  else:
    args = [node_obj.get_current_id()] + list(args)
  url = urlresolvers.reverse(view_func_name, args=args, kwargs=kwargs)
  return http.HttpResponseRedirect(url)

def node_argument(function=None, try_ip=False):
  """
  A decorator for views which accept `web.nodes.models.Node` object as the first argument. It translates possible
  identificators (primary key/uuid, name and optionally ip) into Node object so view wrapped with this decorator
  gets object as an argument. If it exists.
  
  For requests with POST method we require that node is specified with primary key/uuid. For other we prefer name and
  redirect to it if it is not name. (Only for invalid/unknown nodes we allow primary key/uuid).
  """
  
  def decorator(view_func):
    def _wrapped_view(request, node, *args, **kwargs):
      if request.method == 'POST':
        # In POST request we require node to be primary key
        node_obj = shortcuts.get_object_or_404(models.Node, pk=node)
      else:
        # In GET request we redirect if node is primary key
        try:
          node_obj = models.Node.objects.get(name=node)
        except models.Node.DoesNotExist:
          # We try primary key
          try:
            if try_ip:
              node_obj = models.Node.objects.get(pk=node)
            else:
              node_obj = shortcuts.get_object_or_404(models.Node, pk=node)
            if not node_obj.is_invalid():
              # We redirect if node is not invalid (unknown) and was accessed by primary key
              return redirect_helper(view_func, node_obj, *args, **kwargs)
          except models.Node.DoesNotExist:
            # Try also IP and redirect if found
            node_obj = shortcuts.get_object_or_404(models.Node, ip=node)
            return redirect_helper(view_func, node_obj, *args, **kwargs)
      return view_func(request, node_obj, *args, **kwargs)

    wrapped_view_func = wraps(view_func, assigned=decorators.available_attrs(view_func))(_wrapped_view)
    return wrapped_view_func

  if function:
    return decorator(function)
  return decorator

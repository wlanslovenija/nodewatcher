from django.conf import settings
from django.contrib.sites.models import Site
from web.nodes.models import Subnet

def web_client_node(request):
  """
  Adds web_client_node variable to current template context
  depending on whether the current client's IP address is from
  a node's allocated subnet.
  """
  try:
    subnet = Subnet.objects.ip_filter(ip_subnet__contains = request.META["REMOTE_ADDR"]).exclude(cidr = 0)[0]
    node = subnet.node
  except IndexError:
    node = None
  
  return {
    'web_client_node' : node
  }

def global_values(request):
  """
  Adds some global values to the context.
  """
  return {
    'network' : {
      'name'         : settings.NETWORK_NAME,
      'home'         : settings.NETWORK_HOME,
      'contact'      : settings.NETWORK_CONTACT,
      'contact_page' : settings.NETWORK_CONTACT_PAGE,
      'description'  : getattr(settings, 'NETWORK_DESCRIPTION', None),
      'favicon_url'  : settings.NETWORK_FAVICON_URL,
      'logo_url'     : settings.NETWORK_LOGO_URL,
    },
    'request' : {
      'path' : request.path,
    },
    'base_url'                  : "%s://%s" % ('https' if getattr(settings, 'USE_HTTPS', None) else 'http', Site.objects.get_current().domain),
    'feeds_base_url'            : "%s://%s" % ('https' if getattr(settings, 'FEEDS_USE_HTTPS', None) else 'http', Site.objects.get_current().domain),
    'images_bindist_url'        : getattr(settings, 'IMAGES_BINDIST_URL', None),
    'documentation_links'       : getattr(settings, 'DOCUMENTATION_LINKS', {}),
    'stickers_enabled'          : getattr(settings, 'STICKERS_ENABLED', False),
    'generator_enabled'         : getattr(settings, 'IMAGE_GENERATOR_ENABLED', False) or \
                                  getattr(settings, 'DEBUG', False)
  }


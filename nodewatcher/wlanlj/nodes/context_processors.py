from wlanlj.nodes.models import Subnet

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


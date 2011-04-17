from django.utils.translation import ugettext as _

from core.cgm import base as cgm_base
from registry import registration

@cgm_base.register_platform_module("openwrt", 50)
def openvpn(node, cfg):
  """
  Generates configuration for OpenVPN.
  """
  # TODO
  pass

# Add OpenVPN to list of supported VPN solutions
registration.register_choice("core.vpn.server#protocol", "openvpn", _("OpenVPN"))


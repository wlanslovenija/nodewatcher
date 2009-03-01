from django import forms
from django.utils.translation import ugettext as _
from wlanlj.generator.models import Template, Profile
from wlanlj.nodes import ipcalc
from datetime import datetime
import re

IPV4_ADDR_RE = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')

class GenerateImageForm(forms.Form):
  """
  A simple form for image generation.
  """
  wan_dhcp = forms.BooleanField(required = False, label = _("WAN auto-configuration (DHCP)"))
  wan_ip = forms.CharField(max_length = 45, required = False, label = _("WAN IP/mask"))
  wan_gw = forms.CharField(max_length = 40, required = False, label = _("WAN GW"))

  def clean(self):
    """
    Additional validation handler.
    """
    wan_dhcp = self.cleaned_data.get('wan_dhcp')
    wan_ip = self.cleaned_data.get('wan_ip')
    wan_gw = self.cleaned_data.get('wan_gw')

    if not wan_dhcp and (not wan_ip or not wan_gw):
      raise forms.ValidationError(_("IP and gateway are required for static WAN configuration!"))

    if wan_ip:
      try:
        network, cidr = wan_ip.split('/')
        cidr = int(cidr)
        if not IPV4_ADDR_RE.match(network) or network.startswith('127.'):
          raise ValueError
      except ValueError:
        raise forms.ValidationError(_("Enter subnet in CIDR notation!")) 
      
      if not IPV4_ADDR_RE.match(wan_gw) or wan_gw.startswith('127.'):
        raise forms.ValidationError(_("Enter a valid gateway IP address!"))

      self.cleaned_data['wan_ip'] = network
      self.cleaned_data['wan_cidr'] = cidr

      net = ipcalc.Network(str(ipcalc.Network(network, cidr).network()), cidr)
      if ipcalc.IP(wan_gw) not in net:
        raise forms.ValidationError(_("Gateway must be part of specified WAN subnet!"))

    return self.cleaned_data
  
  def save(self, node):
    """
    Saves modifiable stuff into the profile
    """
    node.profile.wan_dhcp = self.cleaned_data.get('wan_dhcp')
    node.profile.wan_ip = self.cleaned_data.get('wan_ip')
    node.profile.wan_cidr = self.cleaned_data.get('wan_cidr')
    node.profile.wan_gw = self.cleaned_data.get('wan_gw')
    node.profile.save()


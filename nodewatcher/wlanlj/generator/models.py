from django.db import models
from django.contrib.auth.models import User
from wlanlj.nodes.models import Node, Subnet as SubnetAllocation
from wlanlj.generator.types import IfaceType
import os

class ImageFile(models.Model):
  """
  This class represents an image filename for template.
  """
  name = models.CharField(max_length = 200)
  type = models.CharField(max_length = 20, null = True) # type should be null if template has only one image file type
  
  def __unicode__(self):
    """
    Return human readable image filename.
    """
    return self.name

class Template(models.Model):
  """
  This class represents a preconfigured profile for image generation. This
  corresponds to options passed on to the image generator.
  """
  name = models.CharField(max_length = 50)
  short_name = models.CharField(max_length = 50)
  description = models.CharField(max_length = 200)
  experimental = models.BooleanField(default = False)

  # Profile metadata for the generator
  openwrt_version = models.CharField(max_length = 20)
  arch = models.CharField(max_length = 20)
  iface_wifi = models.CharField(max_length = 10)
  iface_lan = models.CharField(max_length = 10)
  iface_wan = models.CharField(max_length = 10)
  driver = models.CharField(max_length = 20)
  channel = models.IntegerField()
  port_layout = models.CharField(max_length = 20)
  imagebuilder = models.CharField(max_length = 100)
  imagefiles = models.ManyToManyField(ImageFile)

  def __unicode__(self):
    """
    Return human readable template name.
    """
    return self.name

class IfaceTemplate(models.Model):
  """
  Interface templates.
  """
  template = models.ForeignKey(Template)
  type = models.IntegerField()
  ifname = models.CharField(max_length = 15)

  def __unicode__(self):
    """
    Returns human readable interface type name.
    """
    if self.type == IfaceType.LAN:
      return "LAN"
    elif self.type == IfaceType.WAN:
      return "WAN"
    elif self.type == IfaceType.WiFi:
      return "WiFi"
    else:
      return "Unknown"

class OptionalPackage(models.Model):
  """
  This class represents an optional package that can be enabled by the
  user in their profile.
  """
  fancy_name = models.CharField(max_length = 200)
  description = models.CharField(max_length = 200)
  name = models.CharField(max_length = 100)

  def __unicode__(self):
    """
    Returns a string representation of this model.
    """
    return "%s (%s)" % (self.fancy_name, self.description)

class Profile(models.Model):
  """
  This class represents an actual user's configuration profile.
  """
  template = models.ForeignKey(Template)
  node = models.OneToOneField(Node)

  # Specialization information
  channel = models.IntegerField()
  root_pass = models.CharField(max_length = 20)
  use_vpn = models.BooleanField()
  use_captive_portal = models.BooleanField()
  antenna = models.IntegerField(default = 4)

  # LAN bridge option
  lan_bridge = models.BooleanField(default = False)

  # Static WAN configuration
  wan_dhcp = models.BooleanField(default = True)
  wan_ip = models.CharField(max_length = 40, null = True)
  wan_cidr = models.IntegerField(null = True)
  wan_gw = models.CharField(max_length = 40, null = True)

  # Optional packages
  optional_packages = models.ManyToManyField(OptionalPackage)

  # VPN upload shaping
  vpn_egress_limit = models.IntegerField(null = True)

def gen_mac_address():
  """
  Generates a random MAC address.
  """
  mac = [ord(x) for x in os.urandom(4)]
  return "00:ff:%02x:%02x:%02x:%02x" % tuple(mac)


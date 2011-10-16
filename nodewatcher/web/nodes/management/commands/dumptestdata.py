import gc
import os
import random
import sys
import StringIO as string_io
import subprocess

from django.conf import settings
from django.core import management
from django.core.management import base as management_base
from django.core import serializers

from web.nodes import ipcalc

# TODO: Make temporary directory configurable

# TODO: Maybe use Python libraries instead of external command invocations 

# TODO: Change all prints to self.stdout.write for Django 1.3

def generate_random_ip():
  """
  Generates a random (but valid) IP address.
  """
  return ".".join([str(random.choice(range(1, 255))) for i in xrange(4)])

class Command(management_base.BaseCommand):
  """
  This class defines a command for manage.py which generates a
  sanitized dump of the nodewatcher database.
  """
  args = "<dump_archive>"
  help = "Generates a sanitized dump of the nodewatcher database."
  
  def handle(self, *args, **options):
    """
    Generates a sanitized dump of the nodewatcher database.
    """
    if len(args) != 1:
      raise management_base.CommandError('Missing dump archive argument!')
    
    # Transform a relative path into an absolute one
    dest_archive = args[0]
    if dest_archive != '/':
      dest_archive = os.path.join(os.getcwd(), dest_archive)
    
    # A hack to get dumpdata output
    json = string_io.StringIO()
    sys.stdout = json
    management.call_command("dumpdata")
    sys.stdout = sys.__stdout__
    gc.collect()
    
    # Get JSON and sanitize the dump
    json.seek(0)
    
    def ensure_success(errcode):
      if errcode != 0:
        raise management_base.CommandError('Command failed to execute, aborting!')
    
    def object_transformator():
      """
      Object transformator generator.
      """
      # Read all objects one by one
      for holder in serializers.deserialize("json", json):
        object = holder.object
        name = "%s.%s" % (object.__module__, object.__class__.__name__)
        
        # Some objects need to be sanitized
        if name == 'web.nodes.models.Node':
          if not object.is_dead():
            # We do not clean notes for dead nodes as they explain death background
            object.notes = ''
        elif name == 'web.account.models.UserAccount':
          object.vpn_password = 'XXX'
          object.name = ""
          object.phone = '5551234'
        elif name == 'django.contrib.auth.models.User':
          object.first_name = ""
          object.last_name = ""
          object.email = "user@example.net"
          object.password = '$1$1qL5F...$ZPQdHpHMsvNQGI4rIbAG70' # Password for all users is 123
        elif name == 'web.generator.models.Profile':
          object.root_pass = 'XXXX'
          if not object.wan_dhcp:
            object.wan_ip = generate_random_ip()
            object.wan_cidr = 24
            net = ipcalc.Network(object.wan_ip, object.wan_cidr)
            object.wan_gw = str(net.host_first())
        elif name == 'web.generator.models.StatsSolar':
          continue
        elif name == 'web.generator.models.WhitelistItem':
          continue
        elif name == 'django.contrib.sessions.models.Session':
          continue
        elif name == 'django.contrib.auth.models.Message':
          continue

        yield holder.object
    
    # Perform dump transformation
    tmp_dir = os.path.join("/tmp", ".__nodewatcher_dump_dir")
    ensure_success(subprocess.call(["rm", "-rf", tmp_dir]))
    os.mkdir(tmp_dir)
    
    out = open(os.path.join(tmp_dir, "data.json"), "w")
    serializers.serialize("json", object_transformator(), stream = out)
    out.close()
    json.close()

    # Copy topology
    ensure_success(subprocess.call([
        "mkdir",
        os.path.join(tmp_dir, "graphs"),
    ]))
    ensure_success(subprocess.call([
        "cp",
        os.path.join(settings.GRAPH_DIR, "network_topology.png"),
        os.path.join(settings.GRAPH_DIR, "network_topology.dot"),
        os.path.join(tmp_dir, "graphs"),
    ]))
    
    # Generate a tar.bz2 archive
    os.chdir(tmp_dir)
    ensure_success(subprocess.call(["tar cfj {0} *".format(dest_archive)], shell = True))
    ensure_success(subprocess.call(["rm", "-rf", tmp_dir]))

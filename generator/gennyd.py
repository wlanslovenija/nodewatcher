#!/usr/bin/python
#
# wlan ljubljana Image Generator Daemon
#
# Copyright (C) 2009 by Jernej Kos <kostko@unimatrix-one.org>
#

# Setup import paths, since we are using Django models
import sys, os
sys.path.append('/var/www/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wlanlj.settings'

# Django stuff
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.template import loader, Context

# Other stuff
from beanstalk import serverconn
from beanstalk import job
from config_generator import OpenWrtConfig, portLayouts
import logging
import hashlib
from traceback import format_exc
import pwd
from zipfile import ZipFile, ZIP_DEFLATED

WORKDIR = "/home/generator"
DESTINATION = "/var/www/nodes.wlan-lj.net/results"
IMAGEBUILDERS = (
  "imagebuilder.atheros",
  "imagebuilder.brcm24",
  "imagebuilder.broadcom",
  "imagebuilder.ar71xx"
)

def no_unicodes(x):
  """
  Converts all unicodes to str instances.
  """
  for k, v in x.iteritems():
    if isinstance(v, unicode):
      x[k] = str(v)

  return x

def generate_image(d):
  """
  Generates an image accoording to given configuration.
  """
  logging.debug(repr(d))

  if d['imagebuilder'] not in IMAGEBUILDERS:
    raise Exception("Invalid imagebuilder specified!")
  
  x = OpenWrtConfig()
  x.setOpenwrtVersion(d['openwrt_ver'])
  x.setArch(d['arch'])
  x.setPortLayout(d['port_layout'])
  x.setWifiIface(d['iface_wifi'], d['driver'], d['channel'])
  x.setWifiAnt(d['rx_ant'], d['tx_ant'])
  x.setLanIface(d['iface_lan'])
  x.setNodeType("adhoc")
  x.setPassword(d['root_pass'])
  x.setHostname(d['hostname'])
  x.setIp(d['ip'])
  x.setSSID(d['ssid'])
  
  # Add WAN interface and all subnets
  if d['wan_dhcp']:
    x.addInterface("wan", d['iface_wan'], init = True)
  else:
    x.addInterface("wan", d['iface_wan'], d['wan_ip'], d['wan_cidr'], d['wan_gw'], init = True)

  for subnet in d['subnets']:
    x.addSubnet(str(subnet['iface']), str(subnet['network']), subnet['cidr'], subnet['dhcp'], True)

  x.setCaptivePortal(d['captive_portal'])
  if d['vpn']:
    x.setVpn(d['vpn_username'], d['vpn_password'])
  
  if d['lan_wifi_bridge']:
    x.enableLanWifiBridge()
  
  if d['lan_wan_switch']:
    x.switchWanToLan()
  
  # Add optional packages
  for package in d['opt_pkg']:
    x.addPackage(package)
  
  # Cleanup stuff from previous builds
  os.chdir(WORKDIR)
  os.system("rm -rf build/files/*")
  os.system("rm -rf build/%s/bin/*" % d['imagebuilder'])
  os.mkdir("build/files/etc")
  x.generate("build/files/etc")

  if d['only_config']:
    # Just pack configuration and send it
    prefix = hashlib.md5(os.urandom(32)).hexdigest()[0:16]
    zip = ZipFile(os.path.join(DESTINATION, prefix + "-config.zip"), 'w', ZIP_DEFLATED)
    os.chdir('build/files')
    for root, dirs, files in os.walk("etc"):
      for file in files:
        zip.write(os.path.join(root, file))
    zip.close()

    # Generate checksum
    f = open(os.path.join(DESTINATION, prefix + "-config.zip"), 'r')
    checksum = hashlib.md5(f.read()).hexdigest()
    f.close()

    # Send an e-mail
    t = loader.get_template('generator/email_config.txt')
    c = Context({
      'hostname'  : d['hostname'],
      'ip'        : d['ip'],
      'username'  : d['vpn_username'],
      'config'    : prefix + "-config.zip",
      'checksum'  : checksum
    })

    send_mail(
      '[wlan-lj] ' + (_("Configuration for %s/%s") % (d['hostname'], d['ip'])),
      t.render(c),
      'generator@wlan-lj.net',
      [d['email']],
      fail_silently = False
    )
  else:
    # Generate full image
    x.build("build/%s" % d['imagebuilder'])

    # Get resulting image
    files = []
    prefix = hashlib.md5(os.urandom(32)).hexdigest()[0:16]
    for file in d['imagefiles']:
      file = str(file)
      os.rename("%s/build/%s/bin/%s" % (WORKDIR, d['imagebuilder'], file), "%s-%s" % (os.path.join(DESTINATION, prefix), file))
      f = open("%s-%s" % (os.path.join(DESTINATION, prefix), file), 'r')
      checksum = hashlib.md5(f.read()).hexdigest()
      f.close()
      files.append({ 'name' : "%s-%s" % (prefix, file), 'checksum' : checksum })

    # Send an e-mail
    t = loader.get_template('generator/email.txt')
    c = Context({
      'hostname'  : d['hostname'],
      'ip'        : d['ip'],
      'username'  : d['vpn_username'],
      'files'     : files
    })

    send_mail(
      '[wlan-lj] ' + (_("Router images for %s/%s") % (d['hostname'], d['ip'])),
      t.render(c),
      'generator@wlan-lj.net',
      [d['email']],
      fail_silently = False
    )

# Configure logger
logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)-8s %(message)s',
                    datefmt = '%a, %d %b %Y %H:%M:%S',
                    filename = '/var/log/wlanlj-gennyd.log',
                    filemode = 'a')

# Change ownership for the build directory
os.system("chown -R generator:generator build")

# Drop user privileges
info = pwd.getpwnam('generator')
os.setgid(info.pw_gid)
os.setuid(info.pw_uid)

logging.info("wlan ljubljana Image Generator Daemon v0.1 starting up...")

c = serverconn.ServerConn("127.0.0.1", 11300)
c.job = job.Job
c.use("generator")

logging.info("Connected to local beanstalkd instance.")

try:
  while True:
    j = c.reserve()

    try:
      logging.info("Generating an image for '%s/%s'..." % (j.data['vpn_username'], j.data['ip']))
      generate_image(no_unicodes(j.data))
      logging.info("Image generation successful!")
    except:
      logging.error(format_exc())
      logging.warning("Image generation has failed!")

      # Send an e-mail
      d = no_unicodes(j.data)
      t = loader.get_template('generator/email-failed.txt')
      ctx = Context({
        'hostname'  : d['hostname'],
        'ip'        : d['ip'],
        'username'  : d['vpn_username']
      })

      send_mail(
        '[wlan-lj] ' + (_("Image generation failed for %s/%s") % (d['hostname'], d['ip'])),
        t.render(ctx),
        'generator@wlan-lj.net',
        [d['email']],
        fail_silently = False
      )

    j.Finish()
except KeyboardInterrupt:
  logging.info("Terminating due to user abort.")
except:
  logging.error(format_exc())
  logging.warning("We are going down!")


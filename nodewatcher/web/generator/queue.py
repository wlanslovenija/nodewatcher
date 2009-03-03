from wlanlj.nodes.models import Node
from wlanlj.generator.models import IfaceTemplate
from wlanlj.account.models import UserAccount
from beanstalk import serverconn
from beanstalk import job

# Global connection instance
queue = serverconn.ServerConn("127.0.0.1", 11300)
queue.use("generator")

def queue_generator_job(node):
  """
  Queues a generator job via the beanstalk daemon.
  """
  assert(isinstance(node, Node))

  # Prepare job metadata from profile information
  subnets = []
  for subnet in node.subnet_set.filter(allocated = True):
    # Resolve actual interface name
    try:
      iface = IfaceTemplate.objects.get(template = node.profile.template, type = subnet.gen_iface_type)
    except IfaceTemplate.DoesNotExist:
      continue

    subnets.append({
      'network'     : subnet.subnet,
      'cidr'        : subnet.cidr,
      'iface'       : iface.ifname,
      'dhcp'        : subnet.gen_dhcp
    })
  
  # Generate VPN password if needed
  profile = UserAccount.for_user(node.owner)
  
  data = {
    'ip'              : node.ip,
    'hostname'        : node.name,
    'vpn_username'    : node.owner.username,
    'vpn_password'    : profile.vpn_password,
    'project'         : node.project.name,
    'ssid'            : node.project.ssid,
    'channel'         : node.profile.channel,
    'rx_ant'          : node.profile.antenna,
    'tx_ant'          : node.profile.antenna,
    'root_pass'       : node.profile.root_pass,
    'vpn'             : node.profile.use_vpn,
    'captive_portal'  : node.profile.use_captive_portal,
    'wan_dhcp'        : node.profile.wan_dhcp,
    'wan_ip'          : node.profile.wan_ip,
    'wan_cidr'        : node.profile.wan_cidr,
    'wan_gw'          : node.profile.wan_gw,
    'lan_wifi_bridge' : node.profile.lan_bridge,
    'openwrt_ver'     : node.profile.template.openwrt_version,
    'arch'            : node.profile.template.arch,
    'iface_wifi'      : node.profile.template.iface_wifi,
    'iface_lan'       : node.profile.template.iface_lan,
    'iface_wan'       : node.profile.template.iface_wan,
    'driver'          : node.profile.template.driver,
    'port_layout'     : node.profile.template.port_layout,
    'imagebuilder'    : node.profile.template.imagebuilder,
    'imagefiles'      : node.profile.template.imagefile.split(","),
    'subnets'         : subnets,
    'email'           : node.owner.email
  }

  # Queue the actual job
  j = job.Job(conn = queue)
  j.data = data
  j.Queue()


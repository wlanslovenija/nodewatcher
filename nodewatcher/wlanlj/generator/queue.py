from wlanlj.nodes.models import Node
from wlanlj.generator.models import IfaceTemplate
from wlanlj.generator.types import IfaceType
from wlanlj.account.models import UserAccount
from django.conf import settings

if settings.ENABLE_IMAGE_GENERATOR:
  from beanstalk import serverconn
  from beanstalk import job

def queue_generator_job(node, email_user, config_only = False):
  """
  Queues a generator job via the beanstalk daemon.
  """
  assert(isinstance(node, Node))
  
  if not settings.ENABLE_IMAGE_GENERATOR:
    return

  # Open up a connection with beanstalkd
  queue = serverconn.ServerConn("127.0.0.1", 11300)
  queue.use("generator")

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
    'uuid'            : node.uuid,
    'ip'              : node.ip,
    'hostname'        : node.name,
    'vpn_username'    : node.owner.username,
    'vpn_password'    : profile.vpn_password,
    'vpn_mac'         : node.vpn_mac_conf,
    'project'         : node.project.name,
    'ssid'            : node.project.ssid,
    'channel'         : node.profile.channel,
    'rx_ant'          : node.profile.antenna,
    'tx_ant'          : node.profile.antenna,
    'root_pass'       : node.profile.root_pass,
    'vpn'             : node.profile.use_vpn,
    'vpn_limit'       : node.profile.vpn_egress_limit,
    'captive_portal'  : node.profile.use_captive_portal,
    'wan_dhcp'        : node.profile.wan_dhcp,
    'wan_ip'          : node.profile.wan_ip,
    'wan_cidr'        : node.profile.wan_cidr,
    'wan_gw'          : node.profile.wan_gw,
    'lan_wifi_bridge' : node.profile.lan_bridge,
    'openwrt_ver'     : node.profile.template.openwrt_version,
    'router_name'     : node.profile.template.short_name,
    'arch'            : node.profile.template.arch,
    'iface_wifi'      : node.profile.template.iface_wifi,
    'iface_lan'       : node.profile.template.iface_lan,
    'iface_wan'       : node.profile.template.iface_wan,
    'driver'          : node.profile.template.driver,
    'port_layout'     : node.profile.template.port_layout,
    'imagebuilder'    : node.profile.template.imagebuilder,
    'imagefiles'      : [(x.name, x.type) for x in node.profile.template.imagefiles.all()],
    'opt_pkg'         : [x.name for x in node.profile.optional_packages.all()],
    'subnets'         : subnets,
    'lan_wan_switch'  : not node.profile.template.iface_lan and node.has_allocated_subnets(IfaceType.LAN),
    'only_config'     : config_only,
    'email'           : email_user.email
  }

  # Queue the actual job
  j = job.Job(conn = queue)
  j.data = data
  j.Queue()


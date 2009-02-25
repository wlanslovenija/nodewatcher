#!/usr/bin/python
#
# wlan ljubljana configuration generator
#
# Copyright (C) 2008 Jernej Kos <kostko@unimatrix-one.org>
#

import os
import ipcalc
import crypt
from datetime import datetime

# A list of driver dependent packages
driverPackages = {
  'broadcom' : ['kmod-brcm-wl', 'kmod-wlcompat', 'wlc'],
  'mac80211' : ['kmod-mac80211', 'kmod-b43'],
  'atheros'  : ['kmod-madwifi']
}

# A list of virtual interface names for some drivers
wifiVirtuals = {
  'atheros'  : 'wifi0'
}

# A list of port layouts (do not forget to add new ones to a list of valid
# layouts to build_image.py if you add them here)
portLayouts = {
               #  LAN           WAN
  'wrt54gl'    : ('0 1 2 3 5*', '4 5'),
  'wrt54gs'    : ('1 2 3 4 5*', '0 5'),
  'whr-hp-g54' : ('1 2 3 4 5*', '0 5'),
  'wl-500g'    : ('1 2 3 4 5*', '0 5'),
  'wl-500gd'   : ('1 2 3 4 5*', '0 5'),
  'fonera'     : None
}

class NodeConfig(object):
  """
  A class representing mesh router configuration.
  """
  ssid = "open.wlan-lj.net"
  bssid = "02:CA:FF:EE:BA:BE"
  arch = "mipsel"
  openwrtVersion = "old"
  wifiVirtualIface = None
  wifiIface = "wl0"
  wifiDriver = "broadcom"
  wifiChannel = 8
  portLayout = "wrt54gl"
  password = "ljw"
  hostname = None
  ip = None
  subnets = None
  vpn = None
  vpnServer = (("91.185.203.243", 9999), ("91.185.199.246", 9999))
  dns = ("10.14.0.2", "10.14.0.3")
  ntp = ("10.14.0.2", "10.14.0.3")
  interfaces = None
  services = None
  captivePortal = False
  dhcpServer = False
  packages = None
  wan = None
  nodeType = "adhoc"
  lanIface = "eth0.0"
  
  def __init__(self):
    """
    Class constructor.
    """
    self.subnets = []
    self.interfaces = []
    self.services = []
    self.packages = []

  def setHostname(self, hostname):
    """
    Sets this node's hostname.
    """
    self.hostname = hostname

  def setIp(self, ip):
    """
    Sets this node's IP.
    """
    self.ip = ip

  def setPassword(self, password):
    """
    Sets the root password.
    """
    self.password = password

  def setWifiIface(self, iface, driver, channel = 8):
    """
    Sets the wireless interface name and driver.
    """
    self.wifiIface = iface
    self.wifiDriver = driver
    self.wifiChannel = channel
    
    if driver in wifiVirtuals:
      self.wifiVirtualIface = wifiVirtuals[driver]
    else:
      self.wifiVirtualIface = iface

  def setLanIface(self, iface):
    """
    Sets the LAN interface name.
    """
    self.lanIface = iface
  
  def setOpenwrtVersion(self, version):
    """
    Sets the OpenWRT version.
    """
    self.openwrtVersion = version
  
  def setArch(self, arch):
    """
    Sets the CPU architecture.
    """
    self.arch = arch
  
  def setPortLayout(self, layout):
    """
    Sets the port layout.
    """
    self.portLayout = layout
  
  def setNodeType(self, nodeType):
    """
    Sets the node type.
    """
    self.nodeType = nodeType

  def setSSID(self, ssid):
    """
    Sets the SSID.
    """
    self.ssid = ssid
  
  def addService(self, priority, name):
    """
    Adds a service to be executed on bootup.
    
    @param priority: Service priority code
    @param name: Service name
    """
    self.services.append({ 'priority' : priority,
                           'name'     : name })
  
  def addInterface(self, id, name, ip = None, cidr = None, gateway = None, init = False, olsr = False, strict = False):
    """
    Adds a non-standard interface to this node.
    
    @param id: Interface configuration identifier
    @param name: Interface name
    @param ip: IP address or None for DHCP
    @param cidr: CIDR or None in case of DHCP
    @param gateway: Gateway or None in case of DHCP
    @param init: True if the iface should be initialized upon boot
    @param olsr: Should OLSR run on this interface
    """
    netmask = None
    
    if ip:
      if not cidr:
        raise Exception('Static IP configuration requires CIDR parameter!')
      
      network = ipcalc.Network("%s/%s" % (ip, cidr))
      netmask = str(network.netmask())
      
      if gateway and gateway not in ipcalc.Network("%s/%s" % (str(network.network()), cidr)):
        raise Exception('Gateway must be in the same network as the given interface!')
    
    self.interfaces.append({ 'name'     : name,
                             'ip'       : ip,
                             'cidr'     : cidr,
                             'mask'     : netmask,
                             'gateway'  : gateway,
                             'id'       : id,
                             'init'     : init,
                             'olsr'     : olsr })
  
  def hasInterface(self, id):
    """
    Returns true if the given interface exists.
    """
    for interface in self.interfaces:
      if interface['id'] == id:
        return True
    
    return False
  
  def getInterface(self, id):
    """
    Returns the interface with the given id.
    """
    for interface in self.interfaces:
      if interface['id'] == id:
        return interface
    
    return None
  
  def getInterfaceByName(self, name):
    """
    Returns the interface with the given name.
    """
    for interface in self.interfaces:
      if interface['name'] == name:
        return interface
    
    return None
  
  def addSubnet(self, interface, subnet, cidr, dhcp = False, olsr = True):
    """
    Adds a subnet to this node.
    
    @param interface: Interface name
    @param subnet: Subnet
    @param cidr: CIDR
    @param dhcp: Should this subnet be announced via DHCP
    @param olsr: Should this subnet be announced via OLSR
    """
    if dhcp:
      self.dhcpServer = True
    
    network = ipcalc.Network("%s/%s" % (subnet, cidr))
    self.subnets.append({ 'interface'   : interface,
                          'subnet'      : subnet,
                          'cidr'        : cidr,
                          'mask'        : str(network.netmask()),
                          'firstIp'     : str(network.host_first()),
                          'rangeStart'  : str(ipcalc.IP(long(network.network()) + 2)),
                          'rangeEnd'    : str(network.host_last()),
                          'dhcp'        : dhcp,
                          'olsr'        : olsr })
  
  def setVpn(self, username, password):
    """
    Sets VPN parameters.
    
    @param username: Assigned username
    @param password: Assigned password
    """
    if not self.hasInterface('wan'):
      raise Exception('VPN requires WAN access configuration!')
    
    self.addInterface('vpn', 'tap0', olsr = True)
    self.vpn = { 'username' : username,
                 'password' : password }
  
  def setCaptivePortal(self, value):
    """
    Toggles the use of a captive portal for internet connections.
    """
    self.captivePortal = value

  def addPackage(self, *args):
    """
    Adds packages to be installed.
    """
    for package in args:
      if package not in self.packages:
        self.packages.append(package)
  
  def generate(self, directory):
    """
    Generates the required configuration files.
    
    @param directory: Path to etc directory
    """
    raise Exception("Missing 'generate' method implementation!")
  
  def build(self, destination):
    """
    Builds the image.
    
    @param destination: Path to image build root
    """
    raise Exception("Missing 'setupPackages' method implementation!")

class OpenWrtConfig(NodeConfig):
  def __init__(self):
    """
    Class constructor.
    """
    NodeConfig.__init__(self)
    
    # Add some basic services
    self.addService('S35', 'misc')
  
  def generate(self, directory):
    """
    Generates the required configuration files for OpenWRT.
    """
    self.base = directory
    os.mkdir(os.path.join(directory, 'init.d'))
    
    # Generate iproute2 rt_tables (hardcoded for now)
    os.mkdir(os.path.join(directory, 'iproute2'))
    f = open(os.path.join(directory, 'iproute2', 'rt_tables'), 'w')
    f.write('8\twan\n')
    f.close()
    
    # Configure HTTP server
    self.__copyServiceTemplate('general/httpd.init', 'httpd')
    os.mkdir(os.path.join(directory, '..', 'www'))
    os.mkdir(os.path.join(directory, '..', 'www', 'cgi-bin'))
    path = os.path.join(directory, '..', 'www', 'cgi-bin', 'urandom')
    self.__copyTemplate("general/httpd.urandom", path)
    os.chmod(path, 0755)
    path = os.path.join(directory, '..', 'www', 'cgi-bin', 'zero')
    self.__copyTemplate("general/httpd.zero", path)
    os.chmod(path, 0755)
    
    # Prevent the date from going to far into the past on reboot
    miscScriptPath = os.path.join(directory, 'init.d', 'misc')
    f = open(miscScriptPath, 'w')
    self.__generateMiscScript(f)
    os.chmod(miscScriptPath, 0755)

    # Setup passwords
    self.__generatePasswords()

    # Create the 'config' directory
    configPath = os.path.join(directory, 'config')
    os.mkdir(configPath)
    
    f = open(os.path.join(configPath, "system"), 'w')
    self.__generateSystemConfig(f)
    
    f = open(os.path.join(configPath, "network"), 'w')
    self.__generateNetworkConfig(f)
    
    f = open(os.path.join(configPath, "wireless"), 'w')
    self.__generateWirelessConfig(f)
    
    f = open(os.path.join(configPath, "ntpclient"), 'w')
    self.__generateNtpClientConfig(f)
    
    # 'dhcp' configuration must be empty, so the init script will use
    # dnsmasq.conf in /etc
    f = open(os.path.join(configPath, "dhcp"), 'w')
    f.close()
    
    # Create the 'olsrd.conf'
    f = open(os.path.join(directory, 'olsrd.conf'), 'w')
    self.__generateOlsrdConfig(f)
    
    # Create the DHCP configuration
    if self.dhcpServer:
      f = open(os.path.join(directory, 'dnsmasq.conf'), 'w')
      self.__generateDhcpServerConfig(f)
    
    # Create the VPN configuration
    if self.vpn:
      self.__generateVpnConfig(os.path.join(directory, 'openvpn'))
    
    # Create the captive portal configuration
    if self.captivePortal and self.dhcpServer:
      self.__generateCaptivePortalConfig(os.path.join(directory, 'nodogsplash'))
    
    # Setup service symlinks
    if self.openwrtVersion == "old":
      self.__generateServices(os.path.join(directory, 'rc.d'))
  
  def build(self, path):
    """
    Build the image using ImageBuilder.
    """
    if self.wifiDriver in driverPackages:
      self.addPackage(*driverPackages[self.wifiDriver])

    self.addPackage('ip', 'olsrd', 'ntpclient', 'wireless-tools', 'kmod-softdog', 'hotplug2', 'cronscripts')
    self.addPackage('nodewatcher', 'olsrd-mod-actions')

    # Build the image
    buildString = 'make image FILES="../files" PACKAGES="-ppp -ppp-mod-pppoe -nas -hostapd-mini %s"' % " ".join(self.packages)
    print buildString
    os.chdir(path)
    os.system(buildString)
  
  def __overwriteService(self, name):
    path = os.path.join(self.base, 'init.d', name)
    open(path, 'w').close()
    os.chmod(path, 0755)
  
  def __copyTemplate(self, name, destination):
    f = open(destination, 'w')
    f.write(open(os.path.join("templates", name), "r").read())
    f.close()
  
  def __copyServiceTemplate(self, template, name):
    path = os.path.join(self.base, 'init.d', name)
    self.__copyTemplate(template, path)
    os.chmod(path, 0755)

  def __generatePasswords(self):
    from random import choice
    import string

    f = open(os.path.join(self.base, 'passwd'), 'w')
    salt = "".join([choice(string.letters + string.digits) for i in xrange(8)])
    f.write('root:%s:0:0:root:/tmp:/bin/ash\n' % crypt.md5crypt(self.password, salt))
    f.write('nobody:*:65534:65534:nobody:/var:/bin/false\n')
    f.close()
  
  def __generateVpnConfig(self, directory):
    os.mkdir(directory)
    
    # Configuration
    f = open(os.path.join(directory, 'wlanlj.conf'), 'w')
    f.write('tls-client\n')
    f.write('proto udp\n')
    f.write('dev tap0\n')
    
    for vpn in self.vpnServer:
      f.write('remote %s %s\n' % vpn)
    
    f.write('resolv-retry infinite\n')
    f.write('nobind\n')
    f.write('persist-key\n')
    f.write('persist-tun\n')
    f.write('ns-cert-type server\n')
    f.write('comp-lzo\n')
    f.write('daemon\n')
    f.write('auth-user-pass /etc/openvpn/wlanlj-password\n')
    f.write('auth-retry nointeract\n')
    f.write('cipher BF-CBC\n')
    f.write('ifconfig %s 255.255.0.0\n' % self.ip)
    f.write('verb 3\n')
    f.write('mute 20\n')
    f.write('user nobody\n')
    f.write('group nogroup\n')
    f.write('ca /etc/openvpn/wlanlj-ca.crt\n')
    f.write('tls-auth /etc/openvpn/wlanlj-ta.key 1\n')
    f.write('up /etc/openvpn/up.sh\n')
    f.close()
    
    # Password file
    f = open(os.path.join(directory, 'wlanlj-password'), 'w')
    f.write(self.vpn['username'] + "\n")
    f.write(self.vpn['password'] + "\n")
    f.close()
    
    # Copy the key and CA templates
    self.__copyTemplate("openvpn/ta.key", os.path.join(directory, 'wlanlj-ta.key'))
    self.__copyTemplate("openvpn/ca.crt", os.path.join(directory, 'wlanlj-ca.crt'))
    
    # Copy the restart script
    self.__copyTemplate("openvpn/up.sh", os.path.join(directory, 'up.sh'))
    os.chmod(os.path.join(directory, 'up.sh'), 0755)

    # Add package dependencies
    self.addPackage('kmod-tun', 'zlib', 'libopenssl', 'liblzo', 'openvpn')
  
  def __generateCaptivePortalConfig(self, directory):
    os.mkdir(directory)
    os.mkdir(os.path.join(directory, 'htdocs'))
    
    # Basic configuration (static)
    f = open(os.path.join(directory, 'nodogsplash.conf'), 'w')
    f.write('GatewayInterface %s\n' % self.wifiIface)
    f.write('GatewayName wlan-lj.net\n')
    
    for subnet in self.subnets:
      if subnet['dhcp'] and subnet['interface'] == self.wifiIface:
        f.write('GatewayIPRange %(subnet)s/%(cidr)s\n' % subnet)
        break
    
    f.write('ClientIdleTimeout 30\n')
    f.write('ClientForceTimeout 360\n')
    f.write('MaxClients 60\n')
    f.write('\n')
    f.write('FirewallRuleSet preauthenticated-users {\n')
    
    for dns in self.dns:
      f.write('  FirewallRule allow tcp port 53 to %s\n' % dns)
      f.write('  FirewallRule allow udp port 53 to %s\n' % dns)
    
    f.write('}\n')
    f.write('\n')
    f.write('FirewallRuleSet authenticated-users {\n')
    # Should be an empty ruleset so nds will use RETURN instead of ACCEPT
    f.write('}\n')
    f.write('\n')
    f.write('FirewallRuleSet users-to-router {\n')
    f.write('  FirewallRule allow\n')
    f.write('}\n')
    f.close()
    
    # Add the nodogsplash service and package dependencies
    self.addService('S50', 'nodogsplash')
    self.addPackage('kmod-ipt-ipopt', 'iptables-mod-ipopt')
    self.addPackage('libpthread', 'nodogsplash')
  
  def __generateDhcpServerConfig(self, f):
    f.write('domain-needed\n')
    f.write('bogus-priv\n')
    f.write('filterwin2k\n')
    f.write('localise-queries\n')
    f.write('no-negcache\n')
    f.write('resolv-file=/tmp/resolv.conf.auto\n')

    for dns in self.dns:
      f.write('server=%s\n' % dns)

    f.write('dhcp-authoritative\n')
    f.write('dhcp-leasefile=/tmp/dhcp.leases\n')
    f.write('\n')
    
    for subnet in self.subnets:
      if subnet['dhcp']:
        subnet['ntp'] = self.ntp[0]
        
        f.write('# %(subnet)s/%(cidr)s\n' % subnet)
        f.write('dhcp-range=%(interface)s,%(rangeStart)s,%(rangeEnd)s,%(mask)s,30m\n' % subnet)
        f.write('dhcp-option=%(interface)s,3,%(firstIp)s\n' % subnet)
        f.write('dhcp-option=%(interface)s,6,%(firstIp)s\n' % subnet)
        f.write('dhcp-option=%(interface)s,42,%(ntp)s\n' % subnet)
    
    f.close()
  
  def __generateMiscScript(self, f):
    f.write('#!/bin/sh /etc/rc.common\n')
    f.write('START=35')
    f.write('\n')
    f.write('start() {\n')
    
    # Prevent the time from reseting to far into the past
    t = datetime.today()
    f.write('\tif [ ! -f /etc/datetime.save ]; then\n')
    f.write('\t  echo -n "%02d%02d%02d%02d%04d" > /etc/datetime.save\n' % (t.month, t.day, t.hour, t.minute, t.year))
    f.write('\tfi\n')
    f.write('\tDT=`cat /etc/datetime.save`\n')
    f.write('\tdate $DT\n')
    f.write('\n')
    
    # Set boot_wait to on if it is not set
    f.write('\tBOOT_WAIT=`nvram get boot_wait`\n')
    f.write('\t[ "$BOOT_WAIT" != "on" ] && {\n')
    f.write('\t  nvram set boot_wait=on\n')
    f.write('\t  nvram commit\n')
    f.write('\t}\n')
    
    f.write('}\n')
    
    f.write('stop() {\n')
    f.write('\tDT=`date +%m%d%H%M%Y`\n')
    f.write('\techo $DT > /etc/datetime.save\n')
    f.write('}\n')
    
    f.close()
    
    if self.openwrtVersion == "old":
      # Copy timezone template
      self.__copyTemplate("general/timezone", os.path.join(self.base, 'TZ'))
  
  def __generateServices(self, directory):
    os.mkdir(directory)
    
    for service in self.services:
      os.symlink("/etc/init.d/%(name)s" % service, os.path.join(directory, "%(priority)s%(name)s" % service))
  
  def __generateOlsrdConfig(self, f):
    # Subnet configuration
    if self.subnets:
      f.write('Hna4\n')
      f.write('{\n')
      
      for subnet in self.subnets:
        if subnet['olsr']:
          f.write('  %(subnet)s  %(mask)s\n' % subnet)
      
      f.write('}\n\n')
    
    # General configuration (static)
    f.write('AllowNoInt yes\n')
    f.write('UseHysteresis no\n')
    f.write('LinkQualityFishEye 0\n')
    f.write('LinkQualityLevel 2\n')
    f.write('LinkQualityWinSize 100\n')
    f.write('Pollrate 0.1\n')
    f.write('TcRedundancy 2\n')
    f.write('MprCoverage 1\n')
    f.write('\n')
    
    # General interface configuration (static)
    def interfaceConfiguration(name):
      f.write('Interface "%s"\n' % name)
      f.write('{\n')
      f.write('  HelloInterval 4.0\n')
      f.write('  HelloValidityTime 80.0\n')
      f.write('  TcInterval 8.0\n')
      f.write('  TcValidityTime 160.0\n')
      f.write('  MidInterval 8.0\n')
      f.write('  MidValidityTime 160.0\n')
      f.write('  HnaInterval 8.0\n')
      f.write('  HnaValidityTime 160.0\n')
      
      # Penalize traffic via VPN
      if name == "tap0":
        f.write('  LinkQualityMult default 0.44\n')
      
      f.write('}\n')
      f.write('\n')
    
    if self.lanIface:
      interfaceConfiguration(self.lanIface)
    
    # Additional interface configuration
    for interface in self.interfaces:
      if interface['olsr']:
        interfaceConfiguration(interface['name'])
    
    f.close()
  
  def __generateSystemConfig(self, f):
    # System configuration
    f.write('config system\n')
    f.write('\toption hostname %s\n' % self.hostname)
    f.write('\toption timezone "CET-1CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00"\n')
    f.write('\n')
    f.close()
  
  def __generateNetworkConfig(self, f):
    # VLAN configuration
    layout = portLayouts[self.portLayout]
    
    if layout:
      f.write('#### VLAN configuration\n')
      f.write('config switch eth0\n')
      f.write('\toption vlan0 "%s"\n' % layout[0])
      f.write('\toption vlan1 "%s"\n' % layout[1])
      f.write('\n')
    
    # Loopback configuration (static)
    f.write('#### Loopback configuration\n')
    f.write('config interface loopback\n')
    f.write('\toption ifname "lo"\n')
    f.write('\toption proto static\n')
    f.write('\toption ipaddr 127.0.0.1\n')
    f.write('\toption netmask 255.0.0.0\n')
    f.write('\n')
    
    # LAN configuration
    if self.lanIface:
      self.addInterface('lan', self.lanIface, self.ip, 16, olsr = True, init = True)
    
    # Add wireless interface configuration
    self.addInterface('mesh', self.wifiIface, self.ip, 16, olsr = (self.nodeType == "adhoc"), init = True)
    
    # Other interfaces configuration
    for interface in self.interfaces:
      if interface['init']:
        f.write('config interface %(id)s\n' % interface)
        f.write('\toption ifname "%(name)s"\n' % interface)
        
        if interface['ip']:
          f.write('\toption proto static\n')
          f.write('\toption ipaddr %(ip)s\n' % interface)
          f.write('\toption netmask %(mask)s\n' % interface)
          
          if interface['gateway']:
            f.write('\toption gateway %(gateway)s\n' % interface)
        else:
          f.write('\toption proto dhcp\n')
        
        f.write('\n')
        
        # Set a fallback IP on WAN interface
        if interface['id'] == 'wan':
          if self.openwrtVersion == "old":
            f.write('config interface fallback\n')
            f.write('\toption ifname "%(name)s:0"\n' % interface)
          else:
            f.write('config alias wanfallback\n')
            f.write('\toption interface wan\n')
          
          f.write('\toption proto static\n')
          f.write('\toption ipaddr 169.254.189.120\n')
          f.write('\toption netmask 255.255.0.0\n')
          f.write('\n')
    
    # VPN route override
    if self.vpn:
      idx = 0
      wanIface = self.getInterface('wan')
      
      for vpn in self.vpnServer:
        f.write('config route vpn%d\n' % idx)
        f.write('\toption interface wan\n')
        f.write('\toption target %s\n' % vpn[0])
        
        # If WAN obtains IP via DHCP, set gateway to 'auto'
        if wanIface['gateway'] == None:
          f.write('\toption gateway auto\n')
        else:
          f.write('\toption gateway %s\n' % wanIface['gateway'])
        
        f.write('\toption metric 0\n')
        f.write('\toption table wan\n')
        f.write('\n')
        idx += 1
    
    # WAN stuff
    if self.hasInterface('wan'):
      f.write('config route wannetwork\n')
      f.write('\toption interface wan\n')
      f.write('\toption target network\n')
      f.write('\toption metric 0\n')
      f.write('\toption table wan\n')
      f.write('\n')
      
      f.write('config route wandefault\n')
      f.write('\toption interface wan\n')
      f.write('\toption target default\n')
      f.write('\toption gateway auto\n')
      f.write('\toption metric 0\n')
      f.write('\toption table wan\n')
      f.write('\n')
    
    # Subnets
    if self.subnets:
      f.write('#### Subnet configuration\n')
      virtualIfaceIds = {}
      
      for subnetId, subnet in enumerate(self.subnets):
        # Generate subnet configuration
        ifaceId = virtualIfaceIds.setdefault(subnet['interface'], 0)
        virtualIfaceIds[subnet['interface']] += 1
        
        if self.openwrtVersion == "old":
          f.write('config interface subnet%d\n' % subnetId)
          f.write('\toption ifname "%s:%d"\n' % (subnet['interface'], ifaceId))
        else:
          f.write('config alias subnet%d\n' % subnetId)
          f.write('\toption interface %(id)s\n' % self.getInterfaceByName(subnet['interface']))
        
        f.write('\toption proto static\n')
        f.write('\toption ipaddr %(firstIp)s\n' % subnet)
        f.write('\toption netmask %(mask)s\n' % subnet)
        f.write('\n')
    
    f.close()
  
  def __generateWirelessConfig(self, f):
    # Wifi device configuration
    f.write('config wifi-device %s\n' % self.wifiVirtualIface)
    f.write('\toption type %s\n' % self.wifiDriver)
    f.write('\toption channel %s\n' % self.wifiChannel)
    f.write('\n')
    
    # Wifi interface configuration
    f.write('config wifi-iface\n')
    f.write('\toption device %s\n' % self.wifiVirtualIface)
    f.write('\toption network mesh\n')
    f.write('\toption mode %s\n' % self.nodeType)
    f.write('\toption ssid %s\n' % self.ssid)
    
    if self.nodeType == "adhoc":
      f.write('\toption bssid %s\n' % self.bssid)
    
    f.write('\toption hidden 0\n')
    f.write('\toption encryption none\n')
    f.write('\n')
    
    f.close()
  
  def __generateNtpClientConfig(self, f):
    # Ntpclient configuration
    for ntp in self.ntp:
      if self.openwrtVersion == "old":
        f.write('config ntpclient\n')
        f.write('\toption count "1"\n')
      else:
        f.write('config ntpserver\n')
      
      f.write('\toption hostname "%s"\n' % ntp)
      f.write('\toption port "123"\n')
      f.write('\n')
    
    if self.openwrtVersion == "new":
      f.write('config ntpdrift\n')
      f.write('\toption freq 0\n')
      f.write('\n')
      
      f.write('config ntpclient\n')
      f.write('\toption interval 60\n')
      f.write('\n')
    
    f.close()
    
    # Add ntpclient service
    self.addService('S80', 'ntpclient')

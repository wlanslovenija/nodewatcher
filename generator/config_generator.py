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
from random import shuffle

# A list of driver dependent packages
driverPackages = {
  'broadcom' : ['kmod-brcm-wl', 'kmod-wlcompat', 'wlc'],
  'mac80211' : ['kmod-mac80211', 'kmod-b43'],
  'atheros'  : ['kmod-madwifi']
}

# A list of platform dependent packages
platformPackages = {
  'rb433'    : ['kmod-switch']
}

# A list of per-platform switch identifiers (when not set, eth0 is used)
switchIds = {
  'rb433'    : '0'
}

# A list of virtual interface names for some drivers
wifiVirtuals = {
  'atheros'  : 'wifi0'
}

# A list of default antenna mappings for some configurations
wifiAntennas = {
                  # Antenna   Force always or only on default
  'fonera'      : (1,         True),
  'fonera+'     : (1,         True),
  'whr-hp-g54'  : (1,         False),
  'wrt54gl'     : (0,         False),
  'wrt54gs'     : (0,         False),
  'wl-500gp'    : (0,         True),
  'wl-500gd'    : (0,         True),
  'rb433'       : (1,         False)
}

# A list of port layouts (do not forget to add new ones to a list of valid
# layouts to build_image.py if you add them here)
portLayouts = {
               #  LAN           WAN
  'wrt54gl'    : ('0 1 2 3 5*', '4 5'),
  'wrt54gs'    : ('1 2 3 4 5*', '0 5'),
  'whr-hp-g54' : ('1 2 3 4 5*', '0 5'),
  'wl-500gp'   : ('0 1 2 3 5*', '4 5'),
  'wl-500gd'   : ('0 1 2 3 5*', '4 5'),
  'fonera'     : None,
  'fonera+'    : True,
  'rb433'      : True # ('1 5*',       '2 5')
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
  wifiTxAnt = 1
  wifiRxAnt = 1
  wifiAntDiv = 0
  portLayout = "wrt54gl"
  password = "ljw"
  hostname = None
  ip = None
  subnets = None
  vpn = None
  vpnServer = (("91.185.203.246", 9999), ("91.185.199.246", 9999))
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
  lanWifiBridge = False
  lanWifiBridgeIface = "br-mesh"
  
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
  
  def setWifiAnt(self, rx, tx):
    """
    Sets the wireless receive/transmit antenna.
    """
    self.wifiRxAnt = rx
    self.wifiTxAnt = tx
    
    if self.wifiRxAnt == self.wifiTxAnt == 3:
      self.wifiAntDiv = 1
    
    if self.portLayout in wifiAntennas:
      ant, force = wifiAntennas[self.portLayout]
      
      if force or rx == tx == 4:
        self.wifiRxAnt = self.wifiTxAnt = ant
  
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
  
  def switchWanToLan(self):
    """
    Changes interface configurations so WAN interfaces takes the role
    of the LAN interface. This will only happen when no VLAN tagging
    is possible (there is no port layout configured for that specified
    configuration).
    
    Also VPN must not be configured, otherwise this method will do
    nothing at all.
    """
    if portLayouts[self.portLayout] or self.vpn or not self.hasInterface('wan'):
      return
    
    wan = self.getInterface('wan')
    self.lanIface = wan['name']
    self.removeInterface('wan')
  
  def enableLanWifiBridge(self):
    """
    Enables LAN<->WiFi bridge.
    """
    # Ignore if  there are any subnets configured for LAN interface
    for subnet in self.subnets:
      if subnet['interface'] == self.lanIface:
        return
    
    self.lanWifiBridge = True
  
  def removeInterface(self, id):
    """
    Removes an interface.
    
    @param id: Interface configuration identifier
    """
    for interface in self.interfaces[:]:
      if interface['id'] == id:
        self.interfaces.remove(interface)
        return
  
  def addInterface(self, id, name, ip = None, cidr = None, gateway = None, init = False, olsr = False, type = None):
    """
    Adds a non-standard interface to this node.
    
    @param id: Interface configuration identifier
    @param name: Interface name
    @param ip: IP address or None for DHCP
    @param cidr: CIDR or None in case of DHCP
    @param gateway: Gateway or None in case of DHCP
    @param init: True if the iface should be initialized upon boot
    @param olsr: Should OLSR run on this interface
    @param type: Optional interface type
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
                             'olsr'     : olsr,
                             'type'     : type })
  
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
    self.addService('K35', 'misc')
  
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
    
    if self.portLayout in platformPackages:
      self.addPackage(*platformPackages[self.portLayout])

    self.addPackage('ip', 'olsrd', 'ntpclient', 'wireless-tools', 'kmod-softdog', 'hotplug2', 'cronscripts')
    self.addPackage('kmod-ipt-conntrack', 'iptables-mod-conntrack')
    self.addPackage('kmod-ipt-nat', 'iptables-mod-nat')
    self.addPackage('nodewatcher', 'olsrd-mod-actions')
    self.addPackage('pv', 'netprofscripts')

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
    f.write('client\n')
    f.write('proto udp\n')
    f.write('dev tap0\n')
    
    vpnServers = list(self.vpnServer)
    shuffle(vpnServers)
    for vpn in vpnServers:
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
    f.close()
    
    # Password file
    f = open(os.path.join(directory, 'wlanlj-password'), 'w')
    f.write(self.vpn['username'] + "\n")
    f.write(self.vpn['password'] + "\n")
    f.close()
    
    # Copy the key and CA templates
    self.__copyTemplate("openvpn/ta.key", os.path.join(directory, 'wlanlj-ta.key'))
    self.__copyTemplate("openvpn/ca.crt", os.path.join(directory, 'wlanlj-ca.crt'))
    
    # Add package dependencies
    self.addPackage('kmod-tun', 'zlib', 'libopenssl', 'liblzo', 'openvpn')
  
  def __generateCaptivePortalConfig(self, directory):
    os.mkdir(directory)
    os.mkdir(os.path.join(directory, 'htdocs'))
    
    # Basic configuration (static)
    f = open(os.path.join(directory, 'nodogsplash.conf'), 'w')
    f.write('GatewayInterface %s\n' % (self.wifiIface if not self.lanWifiBridge else self.lanWifiBridgeIface))
    f.write('GatewayName wlan-lj.net\n')
    
    subnetSize = 30
    for subnet in self.subnets:
      if subnet['dhcp'] and subnet['interface'] == (self.wifiIface if not self.lanWifiBridge else self.lanWifiBridgeIface):
        f.write('GatewayIPRange %(subnet)s/%(cidr)s\n' % subnet)
        subnetSize = ipcalc.Network("%(subnet)s/%(cidr)s" % subnet).size() - 2
        break
    
    f.write('ClientIdleTimeout 30\n')
    f.write('ClientForceTimeout 360\n')
    f.write('MaxClients %d\n' % subnetSize)
    f.write('\n')
    f.write('FirewallRuleSet preauthenticated-users {\n')
    
    for dns in self.dns:
      f.write('  FirewallRule allow tcp port 53 to %s\n' % dns)
      f.write('  FirewallRule allow udp port 53 to %s\n' % dns)
      f.write('  FirewallRule allow icmp to %s\n' % dns)
    
    f.write('}\n')
    f.write('\n')
    f.write('EmptyRuleSetPolicy authenticated-users passthrough\n')
    f.write('EmptyRuleSetPolicy users-to-router passthrough\n')
    f.write('EmptyRuleSetPolicy trusted-users passthrough\n')
    f.write('EmptyRuleSetPolicy trusted-users-to-router passthrough\n')
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
    f.write('STOP=35')
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
    f.write('\tif [ -x /usr/sbin/nvram ]; then\n')
    f.write('\t\tBOOT_WAIT=`nvram get boot_wait`\n')
    f.write('\t\t[ "$BOOT_WAIT" != "on" ] && {\n')
    f.write('\t\t  nvram set boot_wait=on\n')
    f.write('\t\t  nvram commit\n')
    f.write('\t\t}\n')
    f.write('\tfi\n')
    
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
    f.write('LinkQualityAlgorithm "etx_ff"\n')
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
        f.write('  LinkQualityMult default 0.80\n')
      
      f.write('}\n')
      f.write('\n')
    
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
    
    if isinstance(layout, tuple):
      f.write('#### VLAN configuration\n')
      f.write('config switch %s\n' % ("eth0" if not self.portLayout in switchIds else switchIds[self.portLayout]))
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
      # When LAN<->WiFi bridge is enabled, this interface is called 'mesh' as firewall
      # rules for 'mesh' interface should be applied.
      self.addInterface(
        "lan" if not self.lanWifiBridge else "mesh",
        self.lanIface,
        self.ip,
        16,
        olsr = True if not self.lanWifiBridge else False,
        init = True,
        type = None if not self.lanWifiBridge else "bridge"
      )
    
    # Add wireless interface configuration (when no LAN<->WiFi bridge is enabled)
    if not self.lanWifiBridge:
      self.addInterface('mesh', self.wifiIface, self.ip, 16, olsr = (self.nodeType == "adhoc"), init = True)
    else:
      # Transfer all WiFi subnets to bridge interface
      for subnet in self.subnets:
        if subnet['interface'] == self.wifiIface:
          subnet['interface'] = self.lanWifiBridgeIface
      
      # Create a virtual bridge interface (for OLSR configuration)
      self.addInterface("mesh", self.lanWifiBridgeIface, self.ip, 16, olsr = True, init = False)
    
    # Other interfaces configuration
    for interface in self.interfaces:
      if interface['init']:
        f.write('config interface %(id)s\n' % interface)
        f.write('\toption ifname "%(name)s"\n' % interface)
        if interface['type']:
          f.write('\toption type %(type)s\n' % interface)
        
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
    f.write('\toption diversity %s\n' % self.wifiAntDiv)
    f.write('\toption rxantenna %s\n' % self.wifiRxAnt)
    f.write('\toption txantenna %s\n' % self.wifiTxAnt)
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
    f.write('\toption bgscan 0\n')
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
      f.write('\toption interval 3600\n')
      f.write('\n')
    
    f.close()
    
    # Add ntpclient service
    self.addService('S80', 'ntpclient')

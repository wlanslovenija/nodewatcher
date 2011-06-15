# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("generator", "0001_initial"),
        ("policy", "0001_initial"),
        ("core", "0013_null_geolocation"),
        ("cgm", "0010_add_ant_conn"),
        ("solar", "0001_initial"),
        ("digitemp", "0001_initial"),
    )
    
    def forwards(self, orm):
        # Transfer all node configuration from old schema to new one (ignoring Unknown nodes)
        general_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'cgmgeneralconfig')
        sys_role_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'core', model = 'systemroleconfig')
        brouter_role_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'core', model = 'borderrouterroleconfig')
        vpn_role_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'core', model = 'vpnserverroleconfig')
        redundant_role_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'core', model = 'redundantnoderoleconfig')
        ethiface_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'ethernetinterfaceconfig')
        dhcpnetconf_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'dhcpnetworkconfig')
        staticnetconf_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'staticnetworkconfig')
        allocnetconf_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'allocatednetworkconfig')
        vpniface_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'vpninterfaceconfig')
        vpnserver_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'vpnserverconfig')
        wifiiface_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'wifiinterfaceconfig')
        wifinetconf_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'cgm', model = 'wifinetworkconfig')
        solarpkg_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'solar', model = 'cgmsolarpackageconfig')
        digitemppkg_ctype = orm['contenttypes.ContentType'].objects.get(app_label = 'digitemp', model = 'cgmdigitemppackageconfig')
        
        for node in orm.Node.objects.exclude(status = 4):
          print "   > Migrating node:", node.name
          
          # core.general[CgmGeneralConfig]
          general = orm['cgm.CgmGeneralConfig'](root = node, content_type = general_ctype)
          general.name = node.name
          general.location = node.location
          general.project = node.project
          general.notes = node.notes
          general.url = node.url or ""
          
          type_map = {
            1 : "server",
            2 : "wireless",
            3 : "test",
            5 : "mobile",
            6 : "dead"
          }
          general.type = type_map[node.node_type]
          
          general.altitude = 0
          if node.geo_lat is not None:
            general.geolocation = "POINT(%f %f)" % (node.geo_lat, node.geo_long)
          else:
            general.geolocation = None
          
          try:
            profile = orm['generator.Profile'].objects.get(node = node)
          except:
            profile = None
          
          general.version = "stable"
          if profile is not None:
            router_map = {
              "wrt54gl" : "wrt54gl",
              "wrt54gs" : "wrt54gs",
              "whr-hp-g54" : "whr-hp-g54",
              "fonera" : "fon-2100",
              "foneraplus" : "fon-2200",
              "wl-500gp-v1" : "wl500gpv1",
              "wl-500gd" : "wl500gpv1",
              "rb433ah" : "rb433ah",
            }
            general.router = router_map[profile.template.short_name]
            general.platform = "openwrt"
            general.password = profile.root_pass
          else:
            general.platform = ""
            general.router = ""
            general.password = "XXX"
          
          general.save()
          
          # core.roles
          system_node_role = orm['core.SystemRoleConfig'](root = node, content_type = sys_role_ctype)
          system_node_role.system = node.system_node
          system_node_role.save()
          
          border_router_role = orm['core.BorderRouterRoleConfig'](root = node, content_type = brouter_role_ctype)
          border_router_role.border_router = node.border_router
          border_router_role.save()
          
          vpn_server_role = orm['core.VpnServerRoleConfig'](root = node, content_type = vpn_role_ctype)
          vpn_server_role.vpn_server = node.vpn_server
          vpn_server_role.save()
          
          redundant_node_role = orm['core.RedundantNodeRoleConfig'](root = node, content_type = redundant_role_ctype)
          redundant_node_role.redundancy_required = node.redundancy_req
          redundant_node_role.save()
          
          # core.interfaces + core.interfaces.network
          if profile is not None:
            # WiFi
            wifi_iface = orm['cgm.WifiInterfaceConfig'](root = node, content_type = wifiiface_ctype)
            wifi_iface.wifi_radio = "wifi0"
            wifi_iface.protocol = "ieee-80211bg"
            wifi_iface.channel = "ch%d" % profile.channel
            wifi_iface.antenna_connector = "a1"
            try:
              antenna = orm['core.Antenna'].objects.filter(internal_for = general.router)[0]
            except IndexError:
              antenna = None
            
            if node.ant_external or antenna is None:
              antenna = orm['core.Antenna']()
              antenna.name = "Migrated Antenna for '{0}'".format(node.name)
              antenna.manufacturer = "Unknown"
              polarization_map = {
                0 : "horizontal",
                1 : "horizontal",
                2 : "vertical",
                3 : "circular",
                4 : "dual",
              }
              antenna.polarization = polarization_map[node.ant_polarization]
              angle_map = {
                0 : (360, 75),
                1 : (360, 75),
                2 : (180, 75),
                3 : (45, 45),
              }
              antenna.angle_horizontal, antenna.angle_vertical = angle_map[node.ant_type]
              antenna.gain = 8
              antenna.save()
            
            wifi_iface.antenna = antenna
            wifi_iface.save()
            
            # Wireless network config
            wifi_netconf = orm['cgm.WifiNetworkConfig'](root = node, content_type = wifinetconf_ctype)
            wifi_netconf.interface = wifi_iface
            wifi_netconf.enabled = True
            wifi_netconf.description = "Mesh"
            wifi_netconf.role = "mesh"
            wifi_netconf.essid = node.project.ssid
            wifi_netconf.bssid = "02:CA:FF:EE:BA:BE"
            
            wifi_subnet = node.subnet_set.get(gen_iface_type = 2, allocated = True)
            pool = orm['core.Pool'].objects.filter(network = wifi_subnet.subnet, cidr = wifi_subnet.cidr)
            if not pool:
              continue
            
            pool = pool[0]
            while pool.parent is not None:
              pool = pool.parent
            
            wifi_netconf.family = "ipv4"
            wifi_netconf.pool = pool
            wifi_netconf.cidr = wifi_subnet.cidr
            wifi_netconf.usage = "auto"
            wifi_netconf.save()
            
            # WAN (wan0)
            wan_iface = orm['cgm.EthernetInterfaceConfig'](root = node, content_type = ethiface_ctype)
            wan_iface.enabled = True
            wan_iface.eth_port = "wan0"
            wan_iface.save()
            if profile.wan_dhcp:
              # DHCP config
              print "     - Detected DHCP WAN configuration."
              dhcp_netconf = orm['cgm.DHCPNetworkConfig'](root = node, content_type = dhcpnetconf_ctype)
              dhcp_netconf.interface = wan_iface
              dhcp_netconf.enabled = True
              dhcp_netconf.description = "Internet uplink"
              dhcp_netconf.save()
            else:
              # Static config
              print "     - Detected static WAN configuration."
              static_netconf = orm['cgm.StaticNetworkConfig'](root = node, content_type = staticnetconf_ctype)
              static_netconf.interface = wan_iface
              static_netconf.enabled = True
              static_netconf.description = "Internet uplink"
              static_netconf.family = "ipv4"
              static_netconf.address = "{0}/{1}".format(profile.wan_ip, profile.wan_cidr)
              static_netconf.gateway = profile.wan_gw
              static_netconf.save()
            
            # LAN subnets (lan0)
            lan_subnets = []
            for subnet in node.subnet_set.filter(gen_iface_type = 0, allocated = True):
              pool = orm['core.Pool'].objects.filter(network = subnet.subnet, cidr = subnet.cidr)
              if not pool:
                continue
              
              pool = pool[0]
              while pool.parent is not None:
                pool = pool.parent
              
              lan_subnets.append({
                'cidr' : subnet.cidr,
                'pool' : pool
              })
            
            if lan_subnets:
              # Create LAN configuration
              print "     - Detected LAN subnets."
              lan_iface = orm['cgm.EthernetInterfaceConfig'](root = node, content_type = ethiface_ctype)
              lan_iface.enabled = True
              lan_iface.eth_port = "lan0"
              lan_iface.save()
              
              # Create allocated network config for each subnet
              for subnet in lan_subnets:
                alloc_netconf = orm['cgm.AllocatedNetworkConfig'](root = node, content_type = allocnetconf_ctype)
                alloc_netconf.interface = lan_iface
                alloc_netconf.enabled = True
                alloc_netconf.description = "LAN"
                alloc_netconf.family = "ipv4"
                alloc_netconf.pool = subnet['pool']
                alloc_netconf.cidr = subnet['cidr']
                alloc_netconf.usage = "clients"
                alloc_netconf.save()
            
            # VPN
            if profile.use_vpn:
              print "     - Detected VPN tunnel."
              vpn_iface = orm['cgm.VpnInterfaceConfig'](root = node, content_type = vpniface_ctype)
              vpn_iface.enabled = True
              limit_map = {
                128 : "128kbit",
                256 : "256kbit",
                512 : "512kbit",
                1024 : "1mbit",
                2048 : "2mbit",
                4096 : "4mbit",
              }
              vpn_iface.limit_out = limit_map.get(profile.vpn_egress_limit, "")
              try:
                vpn_iface.limit_in = limit_map.get(node.gw_policy.get(addr = node.vpn_mac_conf, family = 1).tc_class.bandwidth, "")
              except orm['policy.Policy'].DoesNotExist:
                vpn_iface.limit_in = ""
              
              vpn_iface.mac = node.vpn_mac_conf
              vpn_iface.save()
              
              # NOTE: Server configuration below was hardcoded in previous versions of nodewatcher,
              # so we need to hardcode it here when doing migrations. These servers are meant for
              # use in the wlan slovenia network.
              
              # VPN servers
              vpn_servers = [
                ("91.185.203.246", 9999),
                ("91.185.199.246", 9999),
              ]
              for host, port in vpn_servers:
                vpn_server = orm['cgm.VpnServerConfig'](root = node, content_type = vpnserver_ctype)
                vpn_server.protocol = "openvpn"
                vpn_server.hostname = host
                vpn_server.port = port
                vpn_server.save()
            
            # core.packages
            for package in profile.optional_packages.all():
              if package.fancy_name == 'solar':
                print "     - Found optional package: solar"
                pkg = orm['solar.CgmSolarPackageConfig'](root = node, content_type = solarpkg_ctype)
                pkg.save()
              elif package.fancy_name == 'digitemp':
                print "     - Found optional package: digitemp"
                pkg = orm['digitemp.CgmDigitempPackageConfig'](root = node, content_type = digitemppkg_ctype)
                pkg.save()
    
    def backwards(self, orm):
        pass

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cgm.allocatednetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'AllocatedNetworkConfig', '_ormbases': ['cgm.CgmNetworkConfig']},
            'cgmnetworkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmNetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'cidr': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'pool': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Pool']"}),
            'usage': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'cgm.cgmgeneralconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmGeneralConfig', '_ormbases': ['core.GeneralConfig']},
            'generalconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.GeneralConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'platform': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#platform'", 'blank': 'True'}),
            'router': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#router'", 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'cgm.cgminterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmInterfaceConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_in': ('web.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#traffic_limits'", 'blank': 'True'}),
            'limit_out': ('web.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#traffic_limits'", 'blank': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_cgminterfaceconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.cgmnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmNetworkConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('web.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'networks'", 'to': "orm['cgm.CgmInterfaceConfig']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_cgmnetworkconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.cgmpackageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmPackageConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_cgmpackageconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.dhcpnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'DHCPNetworkConfig', '_ormbases': ['cgm.CgmNetworkConfig']},
            'cgmnetworkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmNetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.ethernetinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'EthernetInterfaceConfig', '_ormbases': ['cgm.CgmInterfaceConfig']},
            'cgminterfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmInterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'eth_port': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#eth_port'"})
        },
        'cgm.pppoenetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PPPoENetworkConfig', '_ormbases': ['cgm.CgmNetworkConfig']},
            'cgmnetworkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmNetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'cgm.staticnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'StaticNetworkConfig', '_ormbases': ['cgm.CgmNetworkConfig']},
            'address': ('web.registry.fields.IPAddressField', [], {'subnet_required': 'True'}),
            'cgmnetworkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmNetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'gateway': ('web.registry.fields.IPAddressField', [], {'host_required': 'True'})
        },
        'cgm.vpninterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnInterfaceConfig', '_ormbases': ['cgm.CgmInterfaceConfig']},
            'cgminterfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmInterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'mac': ('web.registry.fields.MACAddressField', [], {'auto_add': 'True', 'max_length': '17'})
        },
        'cgm.vpnserverconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnServerConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'protocol': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.vpn.server#protocol'"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_vpnserverconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.wifiinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiInterfaceConfig', '_ormbases': ['cgm.CgmInterfaceConfig']},
            'antenna': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Antenna']", 'null': 'True'}),
            'antenna_connector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '11'}),
            'cgminterfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmInterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'wifi_radio': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_radio'"})
        },
        'cgm.wifinetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiNetworkConfig', '_ormbases': ['cgm.CgmNetworkConfig']},
            'bssid': ('web.registry.fields.MACAddressField', [], {'max_length': '17'}),
            'cgmnetworkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmNetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'cidr': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'pool': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Pool']"}),
            'role': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#role'"}),
            'usage': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.allocation': {
            'Meta': {'object_name': 'Allocation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Pool']"})
        },
        'core.antenna': {
            'Meta': {'object_name': 'Antenna'},
            'angle_horizontal': ('django.db.models.fields.IntegerField', [], {'default': '360'}),
            'angle_vertical': ('django.db.models.fields.IntegerField', [], {'default': '360'}),
            'gain': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_for': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'internal_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'polarization': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'core.basicaddressingconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'BasicAddressingConfig'},
            'cidr': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pool': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Pool']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_basicaddressingconfig'", 'to': "orm['nodes.Node']"}),
            'usage': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'core.borderrouterroleconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'BorderRouterRoleConfig', '_ormbases': ['core.RoleConfig']},
            'border_router': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoleConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.generalconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'GeneralConfig'},
            'altitude': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'geolocation': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'project': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['nodes.Project']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_generalconfig'", 'to': "orm['nodes.Node']"}),
            'type': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#type'"}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'core.pool': {
            'Meta': {'object_name': 'Pool'},
            'cidr': ('django.db.models.fields.IntegerField', [], {}),
            'default_prefix_len': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('web.core.allocation.fields.IPField', [], {'null': 'True'}),
            'max_prefix_len': ('django.db.models.fields.IntegerField', [], {'default': '28', 'null': 'True'}),
            'min_prefix_len': ('django.db.models.fields.IntegerField', [], {'default': '24', 'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['core.Pool']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'core.redundantnoderoleconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'RedundantNodeRoleConfig', '_ormbases': ['core.RoleConfig']},
            'redundancy_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoleConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.roleconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'RoleConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_roleconfig'", 'to': "orm['nodes.Node']"})
        },
        'core.systemroleconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'SystemRoleConfig', '_ormbases': ['core.RoleConfig']},
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoleConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.vpnserverroleconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnServerRoleConfig', '_ormbases': ['core.RoleConfig']},
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoleConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'vpn_server': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'digitemp.cgmdigitemppackageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmDigitempPackageConfig', '_ormbases': ['cgm.CgmPackageConfig']},
            'cgmpackageconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmPackageConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dns.zone': {
            'Meta': {'object_name': 'Zone'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'expire': ('django.db.models.fields.IntegerField', [], {}),
            'minimum': ('django.db.models.fields.IntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'primary_ns': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'refresh': ('django.db.models.fields.IntegerField', [], {}),
            'resp_person': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'retry': ('django.db.models.fields.IntegerField', [], {}),
            'serial': ('django.db.models.fields.IntegerField', [], {}),
            'zone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'generator.ifacetemplate': {
            'Meta': {'object_name': 'IfaceTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ifname': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['generator.Template']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'generator.imagefile': {
            'Meta': {'object_name': 'ImageFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'generator.optionalpackage': {
            'Meta': {'object_name': 'OptionalPackage'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fancy_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'generator.profile': {
            'Meta': {'object_name': 'Profile'},
            'antenna': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'channel': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lan_bridge': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'optional_packages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['generator.OptionalPackage']", 'symmetrical': 'False'}),
            'root_pass': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['generator.Template']"}),
            'use_vpn': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vpn_egress_limit': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'wan_cidr': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'wan_dhcp': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'wan_gw': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'wan_ip': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'})
        },
        'generator.profileadaptationchain': {
            'Meta': {'object_name': 'ProfileAdaptationChain'},
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adaptation_chain'", 'to': "orm['generator.Template']"})
        },
        'generator.projectpackage': {
            'Meta': {'object_name': 'ProjectPackage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'packages'", 'to': "orm['nodes.Project']"})
        },
        'generator.template': {
            'Meta': {'object_name': 'Template'},
            'arch': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'channel': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'driver': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'experimental': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iface_lan': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'iface_wan': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'iface_wifi': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'imagebuilder': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'imagefiles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['generator.ImageFile']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'openwrt_version': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'port_layout': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'nodes.apclient': {
            'Meta': {'object_name': 'APClient'},
            'connected_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'downloaded': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'uploaded': ('django.db.models.fields.IntegerField', [], {})
        },
        'nodes.event': {
            'Meta': {'object_name': 'Event'},
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'counter': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need_resend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'source': ('django.db.models.fields.IntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'nodes.eventsubscription': {
            'Meta': {'object_name': 'EventSubscription'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']", 'null': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'nodes.graphitem': {
            'Meta': {'object_name': 'GraphItem'},
            'dead': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'display_priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'graph': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'need_redraw': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'need_removal': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['nodes.GraphItem']"}),
            'rra': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'nodes.installedpackage': {
            'Meta': {'object_name': 'InstalledPackage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'nodes.link': {
            'Meta': {'object_name': 'Link'},
            'dst': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dst'", 'to': "orm['nodes.Node']"}),
            'etx': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ilq': ('django.db.models.fields.FloatField', [], {}),
            'lq': ('django.db.models.fields.FloatField', [], {}),
            'src': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'src'", 'to': "orm['nodes.Node']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'vtime': ('django.db.models.fields.FloatField', [], {})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'ant_external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ant_polarization': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ant_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'awaiting_renumber': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'border_router': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bssid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'captive_portal_status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'channel': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'clients': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'clients_so_far': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'conflicting_subnets': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dns_works': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'firmware_version': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'geo_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'geo_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'loadavg_15min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'loadavg_1min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'loadavg_5min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'local_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'loss_count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'memfree': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True'}),
            'node_type': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'numproc': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'peer_history': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'peer_history_rel_+'", 'to': "orm['nodes.Node']"}),
            'peer_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['nodes.Node']", 'through': "orm['nodes.Link']", 'symmetrical': 'False'}),
            'peers': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'pkt_loss': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'null': 'True', 'to': "orm['nodes.Project']"}),
            'redundancy_link': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redundancy_req': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reported_uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'rtt_avg': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_max': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'system_node': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thresh_frag': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'thresh_rts': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'uptime': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'uptime_last': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'uptime_so_far': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vpn_mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'vpn_mac_conf': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True'}),
            'vpn_server': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'warnings': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wifi_error_count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'wifi_mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'nodes.nodenames': {
            'Meta': {'object_name': 'NodeNames'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'names'", 'to': "orm['nodes.Node']"})
        },
        'nodes.nodewarning': {
            'Meta': {'object_name': 'NodeWarning'},
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'details': ('django.db.models.fields.TextField', [], {}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'warning_list'", 'to': "orm['nodes.Node']"}),
            'source': ('django.db.models.fields.IntegerField', [], {})
        },
        'nodes.project': {
            'Meta': {'object_name': 'Project'},
            'captive_portal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'channel': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'geo_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'geo_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'geo_zoom': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Pool']"}),
            'pools': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['core.Pool']"}),
            'ssid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ssid_backbone': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ssid_mobile': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sticker': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dns.Zone']", 'null': 'True'})
        },
        'nodes.renumbernotice': {
            'Meta': {'object_name': 'RenumberNotice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'renumber_notices'", 'unique': 'True', 'to': "orm['nodes.Node']"}),
            'original_ip': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'renumbered_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'nodes.statssolar': {
            'Meta': {'object_name': 'StatsSolar'},
            'batvoltage': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'charge': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'solvoltage': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'nodes.subnet': {
            'Meta': {'object_name': 'Subnet'},
            'allocated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allocated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'cidr': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'gen_dhcp': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'gen_iface_type': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('web.core.allocation.fields.IPField', [], {'null': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'subnet': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        'nodes.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tweets'", 'to': "orm['nodes.Node']"}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'nodes.whitelistitem': {
            'Meta': {'object_name': 'WhitelistItem'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'registred_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'policy.policy': {
            'Meta': {'object_name': 'Policy'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'addr': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'family': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'gw_policy'", 'to': "orm['nodes.Node']"}),
            'tc_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['policy.TrafficControlClass']"})
        },
        'policy.policyjob': {
            'Meta': {'object_name': 'PolicyJob'},
            'addr': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'family': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'policy.trafficcontrolclass': {
            'Meta': {'object_name': 'TrafficControlClass'},
            'bandwidth': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'solar.cgmsolarpackageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmSolarPackageConfig', '_ormbases': ['cgm.CgmPackageConfig']},
            'cgmpackageconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.CgmPackageConfig']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['core', 'cgm', 'generator', 'policy', 'solar', 'digitemp', 'nodes']

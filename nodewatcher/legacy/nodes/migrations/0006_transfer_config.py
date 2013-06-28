# encoding: utf-8
from django.utils import timezone
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("generator", "0001_initial"),
        ("policy", "0001_initial"),
        ("core", "0024_router_id"),
        ("cgm", "0017_cidr_rename"),
        ("solar", "0002_schema_refactor"),
        ("digitemp", "0002_schema_refactor"),
        ("projects", "0001_initial_p1"),
    )
    needed_by = (
        ("core", "0025_rt_announce_mt"),
        ("cgm", "0018_fkey_details"),
    )

    def get_content_type(self, orm, app_label, model):
        """
        A helper method to get or create content types.
        """
        try:
            return orm['contenttypes.ContentType'].objects.get(app_label = app_label, model = model)
        except orm['contenttypes.ContentType'].DoesNotExist:
            ctype = orm['contenttypes.ContentType'](name = model, app_label = app_label, model = model)
            ctype.save()
            return ctype

    def forwards(self, orm):
        # Transfer all node configuration from old schema to new one (ignoring Unknown nodes)
        general_ctype         = self.get_content_type(orm, 'cgm', 'cgmgeneralconfig')
        project_ctype         = self.get_content_type(orm, app_label = 'projects', model = 'projectconfig')
        loc_ctype             = self.get_content_type(orm, app_label = 'location', model = 'locationconfig')
        desc_ctype            = self.get_content_type(orm, app_label = 'description', model = 'descriptionconfig')
        pwdauth_ctype         = self.get_content_type(orm, app_label = 'cgm', model = 'passwordauthenticationconfig')
        sys_role_ctype        = self.get_content_type(orm, app_label = 'roles', model = 'systemroleconfig')
        brouter_role_ctype    = self.get_content_type(orm, app_label = 'roles', model = 'borderrouterroleconfig')
        vpn_role_ctype        = self.get_content_type(orm, app_label = 'roles', model = 'vpnserverroleconfig')
        redundant_role_ctype  = self.get_content_type(orm, app_label = 'roles', model = 'redundantnoderoleconfig')
        rid_ctype             = self.get_content_type(orm, app_label = 'core', model = 'routeridconfig')
        ethiface_ctype        = self.get_content_type(orm, app_label = 'cgm', model = 'ethernetinterfaceconfig')
        dhcpnetconf_ctype     = self.get_content_type(orm, app_label = 'cgm', model = 'dhcpnetworkconfig')
        staticnetconf_ctype   = self.get_content_type(orm, app_label = 'cgm', model = 'staticnetworkconfig')
        allocnetconf_ctype    = self.get_content_type(orm, app_label = 'cgm', model = 'allocatednetworkconfig')
        vpniface_ctype        = self.get_content_type(orm, app_label = 'cgm', model = 'vpninterfaceconfig')
        vpnserver_ctype       = self.get_content_type(orm, app_label = 'cgm', model = 'vpnserverconfig')
        tpifacelimit_ctype    = self.get_content_type(orm, app_label = 'cgm', model = 'throughputinterfacelimitconfig')
        wifiiface_ctype       = self.get_content_type(orm, app_label = 'cgm', model = 'wifiinterfaceconfig')
        wifinetconf_ctype     = self.get_content_type(orm, app_label = 'cgm', model = 'wifinetworkconfig')
        solarpkg_ctype        = self.get_content_type(orm, app_label = 'solar', model = 'solarpackageconfig')
        digitemppkg_ctype     = self.get_content_type(orm, app_label = 'digitemp', model = 'digitemppackageconfig')

        # Remove all invalid nodes
        orm.Node.objects.filter(status = 4).delete()

        for node in orm.Node.objects.exclude(status = 4):
            print "   > Migrating node:", node.name

            # core.general[CgmGeneralConfig]
            general = orm['cgm.CgmGeneralConfig'](root = node, content_type = general_ctype)
            general.name = node.name

            type_map = {
              1 : "server",
              2 : "wireless",
              3 : "test",
              5 : "mobile",
              6 : "dead"
            }
            general.type = type_map[node.node_type]

            # core.project
            projectcfg = orm['projects.ProjectConfig'](root = node, content_type = project_ctype)
            projectcfg.project = node.project
            projectcfg.save()

            # core.location
            loccfg = orm['location.LocationConfig'](root = node, content_type = loc_ctype)
            loccfg.address = node.location
            loccfg.city = "?"
            loccfg.country = "?"
            loccfg.altitude = 0

            if node.geo_lat is not None:
                loccfg.geolocation = "POINT(%f %f)" % (node.geo_lat, node.geo_long)
            else:
                loccfg.geolocation = None

            loccfg.save()

            # core.description
            dsccfg = orm['description.DescriptionConfig'](root = node, content_type = desc_ctype)
            dsccfg.notes = node.notes
            dsccfg.url = node.url or ""
            dsccfg.save()

            try:
                profile = orm['generator.Profile'].objects.get(node = node)
            except orm['generator.Profile'].DoesNotExist:
                profile = None

            general.version = "stable"
            if profile is not None:
                router_map = {
                    "wrt54g" : "wrt54gl",
                    "wrt54gl" : "wrt54gl",
                    "wrt54gs" : "wrt54gs",
                    "whr-hp-g54" : "whr-hp-g54",
                    "fonera" : "fon-2100",
                    "foneraplus" : "fon-2200",
                    "wl-500gp-v1" : "wl500gpv1",
                    "wl-500gd" : "wl500gpv1",
                    "rb433ah" : "rb433ah",
                    "tp-wr741nd" : "tp-wr741ndv4",
                    "tp-wr740nd" : "tp-wr740nd",
                    "tp-wr842nd" : "tp-wr842nd",
                    "tp-mr3020"  : "tp-mr3020",
                    "tp-wr841nd" : "tp-wr841nd",
                    "tp-wr703n"  : "tp-wr703n",
                    "ub-bullet" : "ub-bullet",
                    "ub-nano" : "ub-nano",
                    "ub-bullet-m5" : "ub-bullet-m5",
                    "ub-rocket-m5" : "ub-rocket-m5",
                    "tp-wr941nd" : "tp-wr941ndv4",
                    "tp-wr1041nd" : "tp-wr1041ndv2",
                    "tp-wr1043nd" : "tp-wr1043ndv1",
                }
                general.router = router_map[profile.template.short_name]
                general.platform = "openwrt"

                pwdcfg = orm['cgm.PasswordAuthenticationConfig'](root = node, content_type = pwdauth_ctype)
                pwdcfg.password = profile.root_pass
                pwdcfg.save()
            else:
                general.platform = ""
                general.router = ""

            general.save()

            # core.roles
            system_node_role = orm['roles.SystemRoleConfig'](root = node, content_type = sys_role_ctype)
            system_node_role.system = node.system_node
            system_node_role.save()

            border_router_role = orm['roles.BorderRouterRoleConfig'](root = node, content_type = brouter_role_ctype)
            border_router_role.border_router = node.border_router
            border_router_role.save()

            vpn_server_role = orm['roles.VpnServerRoleConfig'](root = node, content_type = vpn_role_ctype)
            vpn_server_role.vpn_server = node.vpn_server
            vpn_server_role.save()

            redundant_node_role = orm['roles.RedundantNodeRoleConfig'](root = node, content_type = redundant_role_ctype)
            redundant_node_role.redundancy_required = node.redundancy_req
            redundant_node_role.save()

            # core.routerid
            print "     - Router-ID:", node.ip
            routerid = orm['core.RouterIdConfig'](root = node, content_type = rid_ctype)
            routerid.family = "ipv4"
            routerid.router_id = node.ip
            routerid.save()

            # core.interfaces + core.interfaces.network
            if profile is not None:
                # WiFi
                proto_map = {
                    "wrt54g" : "ieee-80211bg",
                    "wrt54gl" : "ieee-80211bg",
                    "wrt54gs" : "ieee-80211bg",
                    "whr-hp-g54" : "ieee-80211bg",
                    "fonera" : "ieee-80211bg",
                    "foneraplus" : "ieee-80211bg",
                    "wl-500gp-v1" : "ieee-80211bg",
                    "wl-500gd" : "ieee-80211bg",
                    "rb433ah" : "ieee-80211bg",
                    "tp-wr741nd" : "ieee-80211n",
                    "tp-wr740nd" : "ieee-80211n",
                    "tp-wr842nd" : "ieee-80211n",
                    "tp-mr3020"  : "ieee-80211n",
                    "tp-wr841nd" : "ieee-80211n",
                    "tp-wr703n"  : "ieee-80211n",
                    "tp-wr941nd" : "ieee-80211n",
                    "tp-wr1041nd" : "ieee-80211n",
                    "tp-wr1043nd" : "ieee-80211n",
                    "ub-bullet" : "ieee-80211n",
                    "ub-nano" : "ieee-80211n",
                    "ub-bullet-m5" : "ieee-80211n",
                    "ub-rocket-m5" : "ieee-80211n",
                }

                wifi_iface = orm['cgm.WifiInterfaceConfig'](root = node, content_type = wifiiface_ctype)
                wifi_iface.wifi_radio = "wifi0"
                wifi_iface.protocol = proto_map[profile.template.short_name]
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
                pool = orm['core.IpPool'].objects.filter(network = wifi_subnet.subnet, prefix_length = wifi_subnet.cidr)
                if not pool:
                    print "     - WARNING: Primary IP pool not found, skipping network configuration!"
                    continue

                wifi_netconf.allocation = pool = pool[0]
                while pool.parent is not None:
                    pool = pool.parent

                wifi_netconf.family = "ipv4"
                wifi_netconf.pool = pool
                wifi_netconf.prefix_length = wifi_subnet.cidr
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
                    pool = orm['core.IpPool'].objects.filter(network = subnet.subnet, prefix_length = subnet.cidr)
                    if not pool:
                        continue

                    alloc = pool = pool[0]
                    while pool.parent is not None:
                        pool = pool.parent

                    lan_subnets.append({
                      'cidr' : subnet.cidr,
                      'pool' : pool,
                      'allocation' : alloc
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
                        alloc_netconf.prefix_length = subnet['cidr']
                        alloc_netconf.usage = "clients"
                        alloc_netconf.allocation = subnet['allocation']
                        alloc_netconf.save()

                # VPN
                if profile.use_vpn:
                    print "     - Detected VPN tunnel."
                    vpn_iface = orm['cgm.VpnInterfaceConfig'](root = node, content_type = vpniface_ctype)
                    vpn_iface.enabled = True
                    vpn_iface.mac = node.vpn_mac_conf
                    vpn_iface.save()

                    # Interface limits
                    vpn_limit = orm['cgm.ThroughputInterfaceLimitConfig'](root = node, content_type = tpifacelimit_ctype)
                    vpn_limit.interface = vpn_iface
                    limit_map = {
                      128 : "128",
                      256 : "256",
                      512 : "512",
                      1024 : "1024",
                      2048 : "2048",
                      4096 : "4096",
                    }
                    vpn_limit.limit_out = limit_map.get(profile.vpn_egress_limit, "")
                    try:
                        vpn_limit.limit_in = limit_map.get(node.gw_policy.get(addr = node.vpn_mac_conf, family = 1).tc_class.bandwidth, "")
                    except orm['policy.Policy'].DoesNotExist:
                        vpn_limit.limit_in = ""
                    vpn_limit.save()

                    # NOTE: Server configuration below was hardcoded in previous versions of nodewatcher,
                    # so we need to hardcode it here when doing migrations. These servers are meant for
                    # use in the wlan slovenia network.

                    # VPN servers
                    vpn_servers = [
                      ("46.54.226.43", 8942),
                      ("46.54.226.43", 53),
                      ("46.54.226.43", 123),
                      ("91.175.203.240", 8942),
                      ("91.175.203.240", 53),
                      ("91.175.203.240", 123),
                    ]
                    for host, port in vpn_servers:
                        vpn_server = orm['cgm.VpnServerConfig'](root = node, content_type = vpnserver_ctype)
                        vpn_server.protocol = "tunneldigger"
                        vpn_server.hostname = host
                        vpn_server.port = port
                        vpn_server.save()

                # core.packages
                for package in profile.optional_packages.all():
                    if package.fancy_name == 'solar':
                        print "     - Found optional package: solar"
                        pkg = orm['solar.SolarPackageConfig'](root = node, content_type = solarpkg_ctype)
                        pkg.save()
                    elif package.fancy_name == 'digitemp':
                        print "     - Found optional package: digitemp"
                        pkg = orm['digitemp.DigitempPackageConfig'](root = node, content_type = digitemppkg_ctype)
                        pkg.save()
            else:
                # TODO Migrate nodes without profiles (we need to ensure proper interfaces)
                print "     - Node has no profile configured."

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cgm.allocatednetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'AllocatedNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'allocations_cgm_allocatednetworkconfig'", 'null': 'True', 'to': "orm['core.IpPool']"}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'pool': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.IpPool']"}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'usage': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'cgm.authenticationconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'AuthenticationConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_authenticationconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.cgmgeneralconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmGeneralConfig', '_ormbases': ['core.GeneralConfig']},
            'generalconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.GeneralConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'platform': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#platform'", 'blank': 'True'}),
            'router': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#router'", 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'cgm.dhcpnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'DHCPNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.ethernetinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'EthernetInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'eth_port': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#eth_port'"}),
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.interfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_interfaceconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.interfacelimitconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceLimitConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'limits'", 'to': "orm['cgm.InterfaceConfig']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_interfacelimitconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.networkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'networks'", 'to': "orm['cgm.InterfaceConfig']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_networkconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.packageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PackageConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_packageconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.passwordauthenticationconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PasswordAuthenticationConfig', '_ormbases': ['cgm.AuthenticationConfig']},
            'authenticationconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.AuthenticationConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'cgm.pppoenetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PPPoENetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'cgm.publickeyauthenticationconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PublicKeyAuthenticationConfig', '_ormbases': ['cgm.AuthenticationConfig']},
            'authenticationconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.AuthenticationConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'public_key': ('django.db.models.fields.TextField', [], {})
        },
        'cgm.staticnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'StaticNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'address': ('nodewatcher.core.registry.fields.IPAddressField', [], {'subnet_required': 'True'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'gateway': ('nodewatcher.core.registry.fields.IPAddressField', [], {'host_required': 'True'}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.throughputinterfacelimitconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'ThroughputInterfaceLimitConfig', '_ormbases': ['cgm.InterfaceLimitConfig']},
            'interfacelimitconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceLimitConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'limit_in': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.limits#speeds'", 'blank': 'True'}),
            'limit_out': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.limits#speeds'", 'blank': 'True'})
        },
        'cgm.vpninterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'mac': ('nodewatcher.core.registry.fields.MACAddressField', [], {'auto_add': 'True', 'max_length': '17'})
        },
        'cgm.vpnserverconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnServerConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.vpn.server#protocol'"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_vpnserverconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.wifiinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'antenna': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Antenna']", 'null': 'True'}),
            'antenna_connector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '11'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'wifi_radio': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_radio'"})
        },
        'cgm.wifinetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'allocations_cgm_wifinetworkconfig'", 'null': 'True', 'to': "orm['core.IpPool']"}),
            'bssid': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'pool': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.IpPool']"}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'role': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#role'"}),
            'usage': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'Meta': {'object_name': 'BasicAddressingConfig'},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'allocations_core_basicaddressingconfig'", 'null': 'True', 'to': "orm['core.IpPool']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pool': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.IpPool']"}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_basicaddressingconfig'", 'to': "orm['nodes.Node']"}),
            'usage': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'roles.borderrouterroleconfig': {
            'Meta': {'object_name': 'BorderRouterRoleConfig', '_ormbases': ['roles.RoleConfig']},
            'border_router': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['roles.RoleConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.generalconfig': {
            'Meta': {'object_name': 'GeneralConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_generalconfig'", 'to': "orm['nodes.Node']"}),
            'type': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#type'"})
        },
        'core.generalmonitor': {
            'Meta': {'object_name': 'GeneralMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_generalmonitor'", 'to': "orm['nodes.Node']"})
        },
        'core.ippool': {
            'Meta': {'object_name': 'IpPool'},
            'allocation_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'allocation_object_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'allocation_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('django.db.models.fields.CharField', [], {'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['core.IpPool']"}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {}),
            'prefix_length_default': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'prefix_length_maximum': ('django.db.models.fields.IntegerField', [], {'default': '28', 'null': 'True'}),
            'prefix_length_minimum': ('django.db.models.fields.IntegerField', [], {'default': '24', 'null': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pools_core_ippool'", 'symmetrical': 'False', 'to': "orm['nodes.Project']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'location.locationconfig': {
            'Meta': {'object_name': 'LocationConfig'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'altitude': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'geolocation': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_locationconfig'", 'to': "orm['nodes.Node']"})
        },
        'roles.redundantnoderoleconfig': {
            'Meta': {'object_name': 'RedundantNodeRoleConfig', '_ormbases': ['roles.RoleConfig']},
            'redundancy_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['roles.RoleConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'roles.roleconfig': {
            'Meta': {'object_name': 'RoleConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_roleconfig'", 'to': "orm['nodes.Node']"})
        },
        'core.routeridconfig': {
            'Meta': {'object_name': 'RouterIdConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.routerid#family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_routeridconfig'", 'to': "orm['nodes.Node']"}),
            'router_id': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.routingtopologymonitor': {
            'Meta': {'object_name': 'RoutingTopologyMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_routingtopologymonitor'", 'to': "orm['nodes.Node']"})
        },
        'core.statusmonitor': {
            'Meta': {'object_name': 'StatusMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'has_warnings': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_statusmonitor'", 'to': "orm['nodes.Node']"}),
            'status': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.monitoring'", 'enum_id': "'core.status#status'"})
        },
        'roles.systemroleconfig': {
            'Meta': {'object_name': 'SystemRoleConfig', '_ormbases': ['roles.RoleConfig']},
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['roles.RoleConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.topologylink': {
            'Meta': {'object_name': 'TopologyLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['core.RoutingTopologyMonitor']"}),
            'peer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['nodes.Node']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_core.topologylink_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"})
        },
        'roles.vpnserverroleconfig': {
            'Meta': {'object_name': 'VpnServerRoleConfig', '_ormbases': ['roles.RoleConfig']},
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['roles.RoleConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'vpn_server': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'digitemp.digitemppackageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'DigitempPackageConfig', '_ormbases': ['cgm.PackageConfig']},
            'packageconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.PackageConfig']", 'unique': 'True', 'primary_key': 'True'})
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
            'ip_subnet': ('django.db.models.fields.CharField', [], {'null': 'True'}),
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
        'solar.solarpackageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'SolarPackageConfig', '_ormbases': ['cgm.PackageConfig']},
            'packageconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.PackageConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'projects.projectconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'ProjectConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['nodes.Project']", 'on_delete': 'models.PROTECT'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_projects_projectconfig'", 'to': "orm['nodes.Node']"})
        },
        'description.descriptionconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'DescriptionConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_descriptionconfig'", 'to': "orm['nodes.Node']"}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['core', 'cgm', 'solar', 'digitemp', 'generator', 'policy', 'nodes']

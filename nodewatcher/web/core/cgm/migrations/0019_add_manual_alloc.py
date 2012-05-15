# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'WifiNetworkConfig.subnet_hint'
        db.add_column('cgm_wifinetworkconfig', 'subnet_hint',
                      self.gf('web.registry.fields.IPAddressField')(null=True),
                      keep_default=False)

        # Adding field 'AllocatedNetworkConfig.subnet_hint'
        db.add_column('cgm_allocatednetworkconfig', 'subnet_hint',
                      self.gf('web.registry.fields.IPAddressField')(null=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'WifiNetworkConfig.subnet_hint'
        db.delete_column('cgm_wifinetworkconfig', 'subnet_hint')

        # Deleting field 'AllocatedNetworkConfig.subnet_hint'
        db.delete_column('cgm_allocatednetworkconfig', 'subnet_hint')

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
            'Meta': {'ordering': "['id']", 'object_name': 'AllocatedNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'allocations_cgm_allocatednetworkconfig'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['core.IpPool']"}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'pool': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.IpPool']", 'on_delete': 'models.PROTECT'}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'subnet_hint': ('web.registry.fields.IPAddressField', [], {'null': 'True'}),
            'usage': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
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
            'platform': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#platform'", 'blank': 'True'}),
            'router': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#router'", 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'cgm.dhcpnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'DHCPNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.ethernetinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'EthernetInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'eth_port': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#eth_port'"}),
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
            'interface': ('web.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'limits'", 'to': "orm['cgm.InterfaceConfig']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_interfacelimitconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.networkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('web.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'networks'", 'to': "orm['cgm.InterfaceConfig']"}),
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
            'address': ('web.registry.fields.IPAddressField', [], {'subnet_required': 'True'}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'gateway': ('web.registry.fields.IPAddressField', [], {'host_required': 'True'}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.throughputinterfacelimitconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'ThroughputInterfaceLimitConfig', '_ormbases': ['cgm.InterfaceLimitConfig']},
            'interfacelimitconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceLimitConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'limit_in': ('web.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.limits#speeds'", 'blank': 'True'}),
            'limit_out': ('web.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.limits#speeds'", 'blank': 'True'})
        },
        'cgm.vpninterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
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
            'Meta': {'ordering': "['id']", 'object_name': 'WifiInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'antenna': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Antenna']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'antenna_connector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '11'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'wifi_radio': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_radio'"})
        },
        'cgm.wifinetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'allocations_cgm_wifinetworkconfig'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['core.IpPool']"}),
            'bssid': ('web.registry.fields.MACAddressField', [], {'max_length': '17'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'pool': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.IpPool']", 'on_delete': 'models.PROTECT'}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'role': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#role'"}),
            'subnet_hint': ('web.registry.fields.IPAddressField', [], {'null': 'True'}),
            'usage': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
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
        'core.generalconfig': {
            'Meta': {'object_name': 'GeneralConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_generalconfig'", 'to': "orm['nodes.Node']"}),
            'type': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#type'"})
        },
        'core.ippool': {
            'Meta': {'object_name': 'IpPool'},
            'allocation_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'allocation_object_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'allocation_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('web.core.allocation.fields.IPField', [], {'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['core.IpPool']"}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {}),
            'prefix_length_default': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'prefix_length_maximum': ('django.db.models.fields.IntegerField', [], {'default': '28', 'null': 'True'}),
            'prefix_length_minimum': ('django.db.models.fields.IntegerField', [], {'default': '24', 'null': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pools_core_ippool'", 'symmetrical': 'False', 'to': "orm['nodes.Project']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
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
        }
    }

    complete_apps = ['cgm']
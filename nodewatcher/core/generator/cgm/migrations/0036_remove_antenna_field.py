# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'WifiRadioDeviceConfig.antenna'
        db.delete_column('cgm_wifiradiodeviceconfig', 'antenna_id')


    def backwards(self, orm):
        # Adding field 'WifiRadioDeviceConfig.antenna'
        db.add_column('cgm_wifiradiodeviceconfig', 'antenna',
                      self.gf('nodewatcher.core.registry.fields.ModelSelectorKeyField')(to=orm['antennas.Antenna'], null=True, on_delete=models.PROTECT),
                      keep_default=False)


    models = {
        'cgm.allocatednetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'AllocatedNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'allocations_cgm_allocatednetworkconfig'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['core.IpPool']"}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'pool': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.IpPool']", 'on_delete': 'models.PROTECT'}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'routing_announce': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#routing_announce'", 'blank': 'True'}),
            'subnet_hint': ('nodewatcher.core.registry.fields.IPAddressField', [], {'host_required': 'True', 'null': 'True', 'blank': 'True'})
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
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'routing_protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#routing_protocol'", 'blank': 'True'}),
            'uplink': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
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
            'mac': ('nodewatcher.core.registry.fields.MACAddressField', [], {'auto_add': 'True', 'max_length': '17'}),
            'protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#vpn_protocol'"}),
            'routing_protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#routing_protocol'", 'blank': 'True'})
        },
        'cgm.vpnnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'address': ('nodewatcher.core.registry.fields.IPAddressField', [], {'host_required': 'True'}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {})
        },
        'cgm.wifiinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'bssid': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17'}),
            'device': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'interfaces'", 'to': "orm['cgm.WifiRadioDeviceConfig']"}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'mode': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_mode'"}),
            'routing_protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#routing_protocol'", 'blank': 'True'})
        },
        'cgm.wifiradiodeviceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiRadioDeviceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'antenna_connector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '11'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'wifi_radio': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_radio'"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.generalconfig': {
            'Meta': {'object_name': 'GeneralConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_generalconfig'", 'to': "orm['nodes.Node']"})
        },
        'core.ippool': {
            'Meta': {'object_name': 'IpPool'},
            'allocation_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'allocation_object_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'allocation_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('nodewatcher.core.registry.fields.IPAddressField', [], {'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['core.IpPool']"}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {}),
            'prefix_length_default': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'prefix_length_maximum': ('django.db.models.fields.IntegerField', [], {'default': '28', 'null': 'True'}),
            'prefix_length_minimum': ('django.db.models.fields.IntegerField', [], {'default': '24', 'null': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pools_core_ippool'", 'symmetrical': 'False', 'to': "orm['nodes.Project']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            'sticker': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['cgm']
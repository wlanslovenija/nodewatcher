# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BridgedNetworkConfig'
        db.create_table(u'cgm_bridgednetworkconfig', (
            (u'networkconfig_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cgm.NetworkConfig'], unique=True, primary_key=True)),
            ('bridge', self.gf('nodewatcher.core.registry.fields.ReferenceChoiceField')(to=orm['cgm.BridgeInterfaceConfig'], null=True, blank=True)),
        ))
        db.send_create_signal(u'cgm', ['BridgedNetworkConfig'])

        # Adding model 'BridgeInterfaceConfig'
        db.create_table(u'cgm_bridgeinterfaceconfig', (
            (u'interfaceconfig_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cgm.InterfaceConfig'], unique=True, primary_key=True)),
            ('routing_protocol', self.gf('nodewatcher.core.registry.fields.SelectorKeyField')(max_length=50, null=True, regpoint='node.config', enum_id='core.interfaces#routing_protocol', blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='A', max_length=30)),
            ('stp', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mac_address', self.gf('nodewatcher.core.registry.fields.MACAddressField')(max_length=17, null=True, blank=True)),
        ))
        db.send_create_signal(u'cgm', ['BridgeInterfaceConfig'])


    def backwards(self, orm):
        # Deleting model 'BridgedNetworkConfig'
        db.delete_table(u'cgm_bridgednetworkconfig')

        # Deleting model 'BridgeInterfaceConfig'
        db.delete_table(u'cgm_bridgeinterfaceconfig')


    models = {
        u'cgm.allocatednetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'AllocatedNetworkConfig', '_ormbases': [u'cgm.NetworkConfig']},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'allocations_cgm_allocatednetworkconfig'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['core.IpPool']"}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            u'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'pool': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.IpPool']", 'on_delete': 'models.PROTECT'}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'routing_announce': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#routing_announce'", 'blank': 'True'}),
            'subnet_hint': ('nodewatcher.core.registry.fields.IPAddressField', [], {'host_required': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'cgm.authenticationconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'AuthenticationConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cgm.authenticationconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'config_cgm_authenticationconfig'", 'to': u"orm['core.Node']"})
        },
        u'cgm.bridgednetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'BridgedNetworkConfig', '_ormbases': [u'cgm.NetworkConfig']},
            'bridge': ('nodewatcher.core.registry.fields.ReferenceChoiceField', [], {'to': u"orm['cgm.BridgeInterfaceConfig']", 'null': 'True', 'blank': 'True'}),
            u'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'cgm.bridgeinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'BridgeInterfaceConfig', '_ormbases': [u'cgm.InterfaceConfig']},
            u'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'mac_address': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '30'}),
            'routing_protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#routing_protocol'", 'blank': 'True'}),
            'stp': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'cgm.cgmgeneralconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmGeneralConfig', '_ormbases': ['core.GeneralConfig']},
            u'generalconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.GeneralConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'platform': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#platform'", 'blank': 'True'}),
            'router': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#router'", 'blank': 'True'}),
            'version': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#version'", 'blank': 'True'})
        },
        u'cgm.dhcpnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'DHCPNetworkConfig', '_ormbases': [u'cgm.NetworkConfig']},
            u'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'cgm.ethernetinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'EthernetInterfaceConfig', '_ormbases': [u'cgm.InterfaceConfig']},
            'eth_port': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#eth_port'"}),
            u'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'mac_address': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17', 'null': 'True', 'blank': 'True'}),
            'routing_protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#routing_protocol'", 'blank': 'True'}),
            'uplink': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'cgm.interfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceConfig'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cgm.interfaceconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'config_cgm_interfaceconfig'", 'to': u"orm['core.Node']"})
        },
        u'cgm.interfacelimitconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceLimitConfig'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'limits'", 'to': u"orm['cgm.InterfaceConfig']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cgm.interfacelimitconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'config_cgm_interfacelimitconfig'", 'to': u"orm['core.Node']"})
        },
        u'cgm.networkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkConfig'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'networks'", 'to': u"orm['cgm.InterfaceConfig']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cgm.networkconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'config_cgm_networkconfig'", 'to': u"orm['core.Node']"})
        },
        u'cgm.packageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PackageConfig'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_cgm.packageconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'config_cgm_packageconfig'", 'to': u"orm['core.Node']"})
        },
        u'cgm.passwordauthenticationconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PasswordAuthenticationConfig', '_ormbases': [u'cgm.AuthenticationConfig']},
            u'authenticationconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.AuthenticationConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'cgm.pppoenetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PPPoENetworkConfig', '_ormbases': [u'cgm.NetworkConfig']},
            u'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'cgm.staticnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'StaticNetworkConfig', '_ormbases': [u'cgm.NetworkConfig']},
            'address': ('nodewatcher.core.registry.fields.IPAddressField', [], {'subnet_required': 'True'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'gateway': ('nodewatcher.core.registry.fields.IPAddressField', [], {'host_required': 'True'}),
            u'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'cgm.throughputinterfacelimitconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'ThroughputInterfaceLimitConfig', '_ormbases': [u'cgm.InterfaceLimitConfig']},
            u'interfacelimitconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.InterfaceLimitConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'limit_in': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.limits#speeds'", 'blank': 'True'}),
            'limit_out': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.limits#speeds'", 'blank': 'True'})
        },
        u'cgm.vpninterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnInterfaceConfig', '_ormbases': [u'cgm.InterfaceConfig']},
            u'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'mac': ('nodewatcher.core.registry.fields.MACAddressField', [], {'auto_add': 'True', 'max_length': '17'}),
            'protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#vpn_protocol'"}),
            'routing_protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#routing_protocol'", 'blank': 'True'})
        },
        u'cgm.vpnnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnNetworkConfig', '_ormbases': [u'cgm.NetworkConfig']},
            'address': ('nodewatcher.core.registry.fields.IPAddressField', [], {'host_required': 'True'}),
            u'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {})
        },
        u'cgm.wifiinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiInterfaceConfig', '_ormbases': [u'cgm.InterfaceConfig']},
            'bssid': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17'}),
            'device': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'interfaces'", 'to': u"orm['cgm.WifiRadioDeviceConfig']"}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'mode': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_mode'"}),
            'routing_protocol': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#routing_protocol'", 'blank': 'True'})
        },
        u'cgm.wifiradiodeviceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiRadioDeviceConfig', '_ormbases': [u'cgm.InterfaceConfig']},
            'ack_distance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'antenna_connector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '11'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'channel_width': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'wifi_radio': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_radio'"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.generalconfig': {
            'Meta': {'object_name': 'GeneralConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_core.generalconfig_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_generalconfig'", 'to': u"orm['core.Node']"})
        },
        'core.ippool': {
            'Meta': {'object_name': 'IpPool'},
            'allocation_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'allocation_object_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'allocation_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('nodewatcher.core.registry.fields.IPAddressField', [], {'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['core.IpPool']"}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {}),
            'prefix_length_default': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'prefix_length_maximum': ('django.db.models.fields.IntegerField', [], {'default': '28', 'null': 'True'}),
            'prefix_length_minimum': ('django.db.models.fields.IntegerField', [], {'default': '24', 'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'core.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        }
    }

    complete_apps = ['cgm']
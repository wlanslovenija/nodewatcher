# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'InterfaceMonitor'
        db.create_table('monitor_interfacemonitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('root', self.gf('django.db.models.fields.related.ForeignKey')(related_name='monitoring_monitor_interfacemonitor', to=orm['core.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('hw_address', self.gf('nodewatcher.core.registry.fields.MACAddressField')(max_length=17)),
            ('tx_packets', self.gf('django.db.models.fields.BigIntegerField')()),
            ('rx_packets', self.gf('django.db.models.fields.BigIntegerField')()),
            ('tx_bytes', self.gf('django.db.models.fields.BigIntegerField')()),
            ('rx_bytes', self.gf('django.db.models.fields.BigIntegerField')()),
            ('tx_errors', self.gf('django.db.models.fields.BigIntegerField')()),
            ('rx_errors', self.gf('django.db.models.fields.BigIntegerField')()),
            ('tx_drops', self.gf('django.db.models.fields.BigIntegerField')()),
            ('rx_drops', self.gf('django.db.models.fields.BigIntegerField')()),
            ('mtu', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('monitor', ['InterfaceMonitor'])

        # Adding model 'WifiInterfaceMonitor'
        db.create_table('monitor_wifiinterfacemonitor', (
            ('interfacemonitor_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['monitor.InterfaceMonitor'], unique=True, primary_key=True)),
            ('mode', self.gf('nodewatcher.core.registry.fields.SelectorKeyField')(max_length=50, regpoint='node.config', enum_id='core.interfaces#wifi_mode')),
            ('essid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('bssid', self.gf('nodewatcher.core.registry.fields.MACAddressField')(max_length=17, null=True)),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('channel', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('channel_width', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('bitrate', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('rts_threshold', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('frag_threshold', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('signal', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('noise', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('snr', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('monitor', ['WifiInterfaceMonitor'])


    def backwards(self, orm):
        # Deleting model 'InterfaceMonitor'
        db.delete_table('monitor_interfacemonitor')

        # Deleting model 'WifiInterfaceMonitor'
        db.delete_table('monitor_wifiinterfacemonitor')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        },
        'monitor.generalresourcesmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'GeneralResourcesMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loadavg_15min': ('django.db.models.fields.FloatField', [], {}),
            'loadavg_1min': ('django.db.models.fields.FloatField', [], {}),
            'loadavg_5min': ('django.db.models.fields.FloatField', [], {}),
            'memory_buffers': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'memory_cache': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'memory_free': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'processes': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_generalresourcesmonitor'", 'to': "orm['core.Node']"})
        },
        'monitor.interfacemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'hw_address': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtu': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_interfacemonitor'", 'to': "orm['core.Node']"}),
            'rx_bytes': ('django.db.models.fields.BigIntegerField', [], {}),
            'rx_drops': ('django.db.models.fields.BigIntegerField', [], {}),
            'rx_errors': ('django.db.models.fields.BigIntegerField', [], {}),
            'rx_packets': ('django.db.models.fields.BigIntegerField', [], {}),
            'tx_bytes': ('django.db.models.fields.BigIntegerField', [], {}),
            'tx_drops': ('django.db.models.fields.BigIntegerField', [], {}),
            'tx_errors': ('django.db.models.fields.BigIntegerField', [], {}),
            'tx_packets': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'monitor.networkresourcesmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkResourcesMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_networkresourcesmonitor'", 'to': "orm['core.Node']"}),
            'routes': ('django.db.models.fields.IntegerField', [], {}),
            'tcp_connections': ('django.db.models.fields.IntegerField', [], {}),
            'udp_connections': ('django.db.models.fields.IntegerField', [], {})
        },
        'monitor.wifiinterfacemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiInterfaceMonitor', '_ormbases': ['monitor.InterfaceMonitor']},
            'bitrate': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'bssid': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17', 'null': 'True'}),
            'channel': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'channel_width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'frag_threshold': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'interfacemonitor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['monitor.InterfaceMonitor']", 'unique': 'True', 'primary_key': 'True'}),
            'mode': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_mode'"}),
            'noise': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rts_threshold': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'signal': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'snr': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['monitor']
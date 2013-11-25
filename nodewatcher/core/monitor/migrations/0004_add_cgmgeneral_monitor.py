# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CgmGeneralMonitor'
        db.create_table('monitor_cgmgeneralmonitor', (
            ('generalmonitor_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.GeneralMonitor'], unique=True, primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('firmware', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
        ))
        db.send_create_signal('monitor', ['CgmGeneralMonitor'])


    def backwards(self, orm):
        # Deleting model 'CgmGeneralMonitor'
        db.delete_table('monitor_cgmgeneralmonitor')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.generalmonitor': {
            'Meta': {'object_name': 'GeneralMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_generalmonitor'", 'to': "orm['core.Node']"})
        },
        'core.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        },
        'monitor.cgmgeneralmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmGeneralMonitor', '_ormbases': ['core.GeneralMonitor']},
            'firmware': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'generalmonitor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.GeneralMonitor']", 'unique': 'True', 'primary_key': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'})
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
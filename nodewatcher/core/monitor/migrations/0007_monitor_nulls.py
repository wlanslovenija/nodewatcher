# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'InterfaceMonitor.rx_packets'
        db.alter_column('monitor_interfacemonitor', 'rx_packets', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=100, decimal_places=0))

        # Changing field 'InterfaceMonitor.name'
        db.alter_column('monitor_interfacemonitor', 'name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'InterfaceMonitor.rx_bytes'
        db.alter_column('monitor_interfacemonitor', 'rx_bytes', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=100, decimal_places=0))

        # Changing field 'InterfaceMonitor.tx_errors'
        db.alter_column('monitor_interfacemonitor', 'tx_errors', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=100, decimal_places=0))

        # Changing field 'InterfaceMonitor.tx_packets'
        db.alter_column('monitor_interfacemonitor', 'tx_packets', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=100, decimal_places=0))

        # Changing field 'InterfaceMonitor.tx_drops'
        db.alter_column('monitor_interfacemonitor', 'tx_drops', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=100, decimal_places=0))

        # Changing field 'InterfaceMonitor.mtu'
        db.alter_column('monitor_interfacemonitor', 'mtu', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'InterfaceMonitor.hw_address'
        db.alter_column('monitor_interfacemonitor', 'hw_address', self.gf('nodewatcher.core.registry.fields.MACAddressField')(max_length=17, null=True))

        # Changing field 'InterfaceMonitor.rx_errors'
        db.alter_column('monitor_interfacemonitor', 'rx_errors', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=100, decimal_places=0))

        # Changing field 'InterfaceMonitor.tx_bytes'
        db.alter_column('monitor_interfacemonitor', 'tx_bytes', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=100, decimal_places=0))

        # Changing field 'InterfaceMonitor.rx_drops'
        db.alter_column('monitor_interfacemonitor', 'rx_drops', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=100, decimal_places=0))

        # Changing field 'NetworkResourcesMonitor.udp_connections'
        db.alter_column('monitor_networkresourcesmonitor', 'udp_connections', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'NetworkResourcesMonitor.tcp_connections'
        db.alter_column('monitor_networkresourcesmonitor', 'tcp_connections', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'NetworkResourcesMonitor.routes'
        db.alter_column('monitor_networkresourcesmonitor', 'routes', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'GeneralResourcesMonitor.processes'
        db.alter_column('monitor_generalresourcesmonitor', 'processes', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'GeneralResourcesMonitor.loadavg_5min'
        db.alter_column('monitor_generalresourcesmonitor', 'loadavg_5min', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'GeneralResourcesMonitor.loadavg_15min'
        db.alter_column('monitor_generalresourcesmonitor', 'loadavg_15min', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'GeneralResourcesMonitor.loadavg_1min'
        db.alter_column('monitor_generalresourcesmonitor', 'loadavg_1min', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'GeneralResourcesMonitor.memory_buffers'
        db.alter_column('monitor_generalresourcesmonitor', 'memory_buffers', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'GeneralResourcesMonitor.memory_cache'
        db.alter_column('monitor_generalresourcesmonitor', 'memory_cache', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'GeneralResourcesMonitor.memory_free'
        db.alter_column('monitor_generalresourcesmonitor', 'memory_free', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'WifiInterfaceMonitor.protocol'
        db.alter_column('monitor_wifiinterfacemonitor', 'protocol', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'WifiInterfaceMonitor.snr'
        db.alter_column('monitor_wifiinterfacemonitor', 'snr', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'WifiInterfaceMonitor.mode'
        db.alter_column('monitor_wifiinterfacemonitor', 'mode', self.gf('nodewatcher.core.registry.fields.SelectorKeyField')(max_length=50, null=True, regpoint='node.config', enum_id='core.interfaces#wifi_mode'))

        # Changing field 'RttMeasurementMonitor.end'
        db.alter_column('monitor_rttmeasurementmonitor', 'end', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'RttMeasurementMonitor.packet_loss'
        db.alter_column('monitor_rttmeasurementmonitor', 'packet_loss', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'RttMeasurementMonitor.successful_packets'
        db.alter_column('monitor_rttmeasurementmonitor', 'successful_packets', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'RttMeasurementMonitor.start'
        db.alter_column('monitor_rttmeasurementmonitor', 'start', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'RttMeasurementMonitor.packet_size'
        db.alter_column('monitor_rttmeasurementmonitor', 'packet_size', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'RttMeasurementMonitor.rtt_maximum'
        db.alter_column('monitor_rttmeasurementmonitor', 'rtt_maximum', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'RttMeasurementMonitor.all_packets'
        db.alter_column('monitor_rttmeasurementmonitor', 'all_packets', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'RttMeasurementMonitor.rtt_minimum'
        db.alter_column('monitor_rttmeasurementmonitor', 'rtt_minimum', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'RttMeasurementMonitor.rtt_average'
        db.alter_column('monitor_rttmeasurementmonitor', 'rtt_average', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'RttMeasurementMonitor.failed_packets'
        db.alter_column('monitor_rttmeasurementmonitor', 'failed_packets', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.rx_packets'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.rx_packets' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.name'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.rx_bytes'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.rx_bytes' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.tx_errors'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.tx_errors' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.tx_packets'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.tx_packets' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.tx_drops'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.tx_drops' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.mtu'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.mtu' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.hw_address'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.hw_address' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.rx_errors'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.rx_errors' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.tx_bytes'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.tx_bytes' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'InterfaceMonitor.rx_drops'
        raise RuntimeError("Cannot reverse this migration. 'InterfaceMonitor.rx_drops' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'NetworkResourcesMonitor.udp_connections'
        raise RuntimeError("Cannot reverse this migration. 'NetworkResourcesMonitor.udp_connections' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'NetworkResourcesMonitor.tcp_connections'
        raise RuntimeError("Cannot reverse this migration. 'NetworkResourcesMonitor.tcp_connections' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'NetworkResourcesMonitor.routes'
        raise RuntimeError("Cannot reverse this migration. 'NetworkResourcesMonitor.routes' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'GeneralResourcesMonitor.processes'
        raise RuntimeError("Cannot reverse this migration. 'GeneralResourcesMonitor.processes' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'GeneralResourcesMonitor.loadavg_5min'
        raise RuntimeError("Cannot reverse this migration. 'GeneralResourcesMonitor.loadavg_5min' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'GeneralResourcesMonitor.loadavg_15min'
        raise RuntimeError("Cannot reverse this migration. 'GeneralResourcesMonitor.loadavg_15min' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'GeneralResourcesMonitor.loadavg_1min'
        raise RuntimeError("Cannot reverse this migration. 'GeneralResourcesMonitor.loadavg_1min' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'GeneralResourcesMonitor.memory_buffers'
        raise RuntimeError("Cannot reverse this migration. 'GeneralResourcesMonitor.memory_buffers' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'GeneralResourcesMonitor.memory_cache'
        raise RuntimeError("Cannot reverse this migration. 'GeneralResourcesMonitor.memory_cache' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'GeneralResourcesMonitor.memory_free'
        raise RuntimeError("Cannot reverse this migration. 'GeneralResourcesMonitor.memory_free' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'WifiInterfaceMonitor.protocol'
        raise RuntimeError("Cannot reverse this migration. 'WifiInterfaceMonitor.protocol' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'WifiInterfaceMonitor.snr'
        raise RuntimeError("Cannot reverse this migration. 'WifiInterfaceMonitor.snr' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'WifiInterfaceMonitor.mode'
        raise RuntimeError("Cannot reverse this migration. 'WifiInterfaceMonitor.mode' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.end'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.end' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.packet_loss'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.packet_loss' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.successful_packets'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.successful_packets' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.start'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.start' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.packet_size'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.packet_size' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.rtt_maximum'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.rtt_maximum' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.all_packets'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.all_packets' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.rtt_minimum'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.rtt_minimum' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.rtt_average'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.rtt_average' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'RttMeasurementMonitor.failed_packets'
        raise RuntimeError("Cannot reverse this migration. 'RttMeasurementMonitor.failed_packets' and its values cannot be restored.")

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
            'loadavg_15min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'loadavg_1min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'loadavg_5min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'memory_buffers': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'memory_cache': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'memory_free': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'processes': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_generalresourcesmonitor'", 'to': "orm['core.Node']"})
        },
        'monitor.interfacemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'hw_address': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtu': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_interfacemonitor'", 'to': "orm['core.Node']"}),
            'rx_bytes': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'rx_drops': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'rx_errors': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'rx_packets': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'tx_bytes': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'tx_drops': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'tx_errors': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'tx_packets': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'})
        },
        'monitor.networkresourcesmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkResourcesMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_networkresourcesmonitor'", 'to': "orm['core.Node']"}),
            'routes': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'tcp_connections': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'udp_connections': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'monitor.rttmeasurementmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'RttMeasurementMonitor'},
            'all_packets': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'failed_packets': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'packet_loss': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'packet_size': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_rttmeasurementmonitor'", 'to': "orm['core.Node']"}),
            'rtt_average': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_maximum': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_minimum': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Node']", 'null': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'successful_packets': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
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
            'mode': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_mode'"}),
            'noise': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'rts_threshold': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'signal': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'snr': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        }
    }

    complete_apps = ['monitor']
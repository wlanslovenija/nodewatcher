# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClientMonitor'
        db.create_table(u'monitor_clientmonitor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_monitor.clientmonitor_set', null=True, to=orm['contenttypes.ContentType'])),
            ('root', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'monitoring_monitor_clientmonitor', to=orm['core.Node'])),
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal(u'monitor', ['ClientMonitor'])

        # Adding model 'ClientAddress'
        db.create_table(u'monitor_clientaddress', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addresses', to=orm['monitor.ClientMonitor'])),
            ('family', self.gf('nodewatcher.core.registry.fields.SelectorKeyField')(max_length=50, null=True, regpoint='node.monitoring', enum_id='core.interfaces.network#family')),
            ('address', self.gf('nodewatcher.core.registry.fields.IPAddressField')()),
            ('expiry_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'monitor', ['ClientAddress'])


    def backwards(self, orm):
        # Deleting model 'ClientMonitor'
        db.delete_table(u'monitor_clientmonitor')

        # Deleting model 'ClientAddress'
        db.delete_table(u'monitor_clientaddress')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        },
        u'monitor.clientaddress': {
            'Meta': {'object_name': 'ClientAddress'},
            'address': ('nodewatcher.core.registry.fields.IPAddressField', [], {}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addresses'", 'to': u"orm['monitor.ClientMonitor']"}),
            'expiry_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.monitoring'", 'enum_id': "'core.interfaces.network#family'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'monitor.clientmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'ClientMonitor'},
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.clientmonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_clientmonitor'", 'to': u"orm['core.Node']"})
        },
        u'monitor.generalmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'GeneralMonitor'},
            'firmware': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.generalmonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_generalmonitor'", 'to': u"orm['core.Node']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'})
        },
        u'monitor.generalresourcesmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'GeneralResourcesMonitor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loadavg_15min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'loadavg_1min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'loadavg_5min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'memory_buffers': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'memory_cache': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'memory_free': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.generalresourcesmonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'processes': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_generalresourcesmonitor'", 'to': u"orm['core.Node']"})
        },
        u'monitor.interfacemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceMonitor'},
            'hw_address': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtu': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.interfacemonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_interfacemonitor'", 'to': u"orm['core.Node']"}),
            'rx_bytes': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'rx_drops': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'rx_errors': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'rx_packets': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'tx_bytes': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'tx_drops': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'tx_errors': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'}),
            'tx_packets': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '100', 'decimal_places': '0'})
        },
        u'monitor.networkaddressmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkAddressMonitor'},
            'address': ('nodewatcher.core.registry.fields.IPAddressField', [], {'null': 'True'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.monitoring'", 'enum_id': "'core.interfaces.network#family'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'networks'", 'to': u"orm['monitor.InterfaceMonitor']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.networkaddressmonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_networkaddressmonitor'", 'to': u"orm['core.Node']"})
        },
        u'monitor.networkresourcesmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkResourcesMonitor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.networkresourcesmonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_networkresourcesmonitor'", 'to': u"orm['core.Node']"}),
            'routes': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'tcp_connections': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'udp_connections': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        u'monitor.routingannouncemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'RoutingAnnounceMonitor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'network': ('nodewatcher.core.registry.fields.IPAddressField', [], {}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.routingannouncemonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_routingannouncemonitor'", 'to': u"orm['core.Node']"}),
            'status': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.monitoring'", 'enum_id': "'network.routing.announces#status'"})
        },
        u'monitor.routingtopologymonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'RoutingTopologyMonitor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.routingtopologymonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_routingtopologymonitor'", 'to': u"orm['core.Node']"})
        },
        u'monitor.rttmeasurementmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'RttMeasurementMonitor'},
            'all_packets': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'failed_packets': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'packet_loss': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'packet_size': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.rttmeasurementmonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_rttmeasurementmonitor'", 'to': u"orm['core.Node']"}),
            'rtt_average': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_maximum': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_minimum': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_std': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Node']", 'null': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'successful_packets': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'monitor.systemstatusmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'SystemStatusMonitor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.systemstatusmonitor_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'monitoring_monitor_systemstatusmonitor'", 'to': u"orm['core.Node']"}),
            'uptime': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        },
        u'monitor.topologylink': {
            'Meta': {'object_name': 'TopologyLink'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': u"orm['monitor.RoutingTopologyMonitor']"}),
            'peer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': u"orm['core.Node']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_monitor.topologylink_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"})
        },
        u'monitor.wifiinterfacemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiInterfaceMonitor', '_ormbases': [u'monitor.InterfaceMonitor']},
            'bitrate': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'bssid': ('nodewatcher.core.registry.fields.MACAddressField', [], {'max_length': '17', 'null': 'True'}),
            'channel': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'channel_width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'frag_threshold': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'interfacemonitor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['monitor.InterfaceMonitor']", 'unique': 'True', 'primary_key': 'True'}),
            'mode': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'null': 'True', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_mode'"}),
            'noise': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'rts_threshold': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'signal': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'snr': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        }
    }

    complete_apps = ['monitor']
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'OlsrRoutingTopologyMonitor.routingtopologymonitor_ptr'
        db.alter_column('olsr_olsrroutingtopologymonitor', 'routingtopologymonitor_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['monitor.RoutingTopologyMonitor'], unique=True, primary_key=True))

        # Changing field 'OlsrRoutingTopologyMonitor.average_etx'
        db.alter_column('olsr_olsrroutingtopologymonitor', 'average_etx', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'OlsrRoutingTopologyMonitor.average_lq'
        db.alter_column('olsr_olsrroutingtopologymonitor', 'average_lq', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'OlsrRoutingTopologyMonitor.average_ilq'
        db.alter_column('olsr_olsrroutingtopologymonitor', 'average_ilq', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'OlsrRoutingAnnounceMonitor.routingannouncemonitor_ptr'
        db.alter_column('olsr_olsrroutingannouncemonitor', 'routingannouncemonitor_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['monitor.RoutingAnnounceMonitor'], unique=True, primary_key=True))

    def backwards(self, orm):

        # Changing field 'OlsrRoutingTopologyMonitor.routingtopologymonitor_ptr'
        db.alter_column('olsr_olsrroutingtopologymonitor', 'routingtopologymonitor_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.RoutingTopologyMonitor'], unique=True, primary_key=True))

        # Changing field 'OlsrRoutingTopologyMonitor.average_etx'
        db.alter_column('olsr_olsrroutingtopologymonitor', 'average_etx', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'OlsrRoutingTopologyMonitor.average_lq'
        db.alter_column('olsr_olsrroutingtopologymonitor', 'average_lq', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'OlsrRoutingTopologyMonitor.average_ilq'
        db.alter_column('olsr_olsrroutingtopologymonitor', 'average_ilq', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'OlsrRoutingAnnounceMonitor.routingannouncemonitor_ptr'
        db.alter_column('olsr_olsrroutingannouncemonitor', 'routingannouncemonitor_ptr_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.RoutingAnnounceMonitor'], unique=True, primary_key=True))

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
        'core.topologylink': {
            'Meta': {'object_name': 'TopologyLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['monitor.RoutingTopologyMonitor']"}),
            'peer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['core.Node']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_core.topologylink_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"})
        },
        'monitor.routingannouncemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'RoutingAnnounceMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'network': ('nodewatcher.core.registry.fields.IPAddressField', [], {}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_routingannouncemonitor'", 'to': "orm['core.Node']"}),
            'status': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.monitoring'", 'enum_id': "'network.routing.announces#status'"})
        },
        'monitor.routingtopologymonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'RoutingTopologyMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_routingtopologymonitor'", 'to': "orm['core.Node']"})
        },
        'olsr.olsrroutingannouncemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'OlsrRoutingAnnounceMonitor', '_ormbases': ['monitor.RoutingAnnounceMonitor']},
            'routingannouncemonitor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['monitor.RoutingAnnounceMonitor']", 'unique': 'True', 'primary_key': 'True'})
        },
        'olsr.olsrroutingtopologymonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'OlsrRoutingTopologyMonitor', '_ormbases': ['monitor.RoutingTopologyMonitor']},
            'average_etx': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'average_ilq': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'average_lq': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'routingtopologymonitor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['monitor.RoutingTopologyMonitor']", 'unique': 'True', 'primary_key': 'True'})
        },
        'olsr.olsrtopologylink': {
            'Meta': {'object_name': 'OlsrTopologyLink', '_ormbases': ['core.TopologyLink']},
            'etx': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'ilq': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'lq': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'topologylink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyLink']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['olsr']
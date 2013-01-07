# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('nodes', '0011_move_node'),
    )

    def forwards(self, orm):

        # Changing field 'NetworkResourcesMonitor.root'
        db.alter_column('monitor_networkresourcesmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'GeneralResourcesMonitor.root'
        db.alter_column('monitor_generalresourcesmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

    def backwards(self, orm):

        # Changing field 'NetworkResourcesMonitor.root'
        db.alter_column('monitor_networkresourcesmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'GeneralResourcesMonitor.root'
        db.alter_column('monitor_generalresourcesmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

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
        'monitor.networkresourcesmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkResourcesMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_networkresourcesmonitor'", 'to': "orm['core.Node']"}),
            'routes': ('django.db.models.fields.IntegerField', [], {}),
            'tcp_connections': ('django.db.models.fields.IntegerField', [], {}),
            'udp_connections': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['monitor']
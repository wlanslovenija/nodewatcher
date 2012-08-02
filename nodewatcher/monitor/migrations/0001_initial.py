# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GeneralResourcesMonitor'
        db.create_table('monitor_generalresourcesmonitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('root', self.gf('django.db.models.fields.related.ForeignKey')(related_name='monitoring_monitor_generalresourcesmonitor', to=orm['nodes.Node'])),
            ('loadavg_1min', self.gf('django.db.models.fields.FloatField')()),
            ('loadavg_5min', self.gf('django.db.models.fields.FloatField')()),
            ('loadavg_15min', self.gf('django.db.models.fields.FloatField')()),
            ('memory_free', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('memory_buffers', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('memory_cache', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('processes', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('monitor', ['GeneralResourcesMonitor'])

        # Adding model 'NetworkResourcesMonitor'
        db.create_table('monitor_networkresourcesmonitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('root', self.gf('django.db.models.fields.related.ForeignKey')(related_name='monitoring_monitor_networkresourcesmonitor', to=orm['nodes.Node'])),
            ('routes', self.gf('django.db.models.fields.IntegerField')()),
            ('tcp_connections', self.gf('django.db.models.fields.IntegerField')()),
            ('udp_connections', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('monitor', ['NetworkResourcesMonitor'])

    def backwards(self, orm):
        # Deleting model 'GeneralResourcesMonitor'
        db.delete_table('monitor_generalresourcesmonitor')

        # Deleting model 'NetworkResourcesMonitor'
        db.delete_table('monitor_networkresourcesmonitor')

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_generalresourcesmonitor'", 'to': "orm['nodes.Node']"})
        },
        'monitor.networkresourcesmonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkResourcesMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_monitor_networkresourcesmonitor'", 'to': "orm['nodes.Node']"}),
            'routes': ('django.db.models.fields.IntegerField', [], {}),
            'tcp_connections': ('django.db.models.fields.IntegerField', [], {}),
            'udp_connections': ('django.db.models.fields.IntegerField', [], {})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        }
    }

    complete_apps = ['monitor']
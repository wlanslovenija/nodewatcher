# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("core", "0025_rt_announce_mt"),
    )

    def forwards(self, orm):
        # Adding model 'OlsrRoutingAnnounceMonitor'
        db.create_table('routing_olsr_olsrroutingannouncemonitor', (
            ('routingannouncemonitor_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.RoutingAnnounceMonitor'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('routing_olsr', ['OlsrRoutingAnnounceMonitor'])

    def backwards(self, orm):
        # Deleting model 'OlsrRoutingAnnounceMonitor'
        db.delete_table('routing_olsr_olsrroutingannouncemonitor')

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.routingannouncemonitor': {
            'Meta': {'object_name': 'RoutingAnnounceMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('web.registry.fields.IPAddressField', [], {}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_routingannouncemonitor'", 'to': "orm['nodes.Node']"}),
            'status': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.monitoring'", 'enum_id': "'network.routing.announces#status'"})
        },
        'core.routingtopologymonitor': {
            'Meta': {'object_name': 'RoutingTopologyMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_routingtopologymonitor'", 'to': "orm['nodes.Node']"})
        },
        'core.topologylink': {
            'Meta': {'object_name': 'TopologyLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['core.RoutingTopologyMonitor']"}),
            'peer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['nodes.Node']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_core.topologylink_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        },
        'routing_olsr.olsrroutingannouncemonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'OlsrRoutingAnnounceMonitor', '_ormbases': ['core.RoutingAnnounceMonitor']},
            'routingannouncemonitor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoutingAnnounceMonitor']", 'unique': 'True', 'primary_key': 'True'})
        },
        'routing_olsr.olsrroutingtopologymonitor': {
            'Meta': {'ordering': "['id']", 'object_name': 'OlsrRoutingTopologyMonitor', '_ormbases': ['core.RoutingTopologyMonitor']},
            'routingtopologymonitor_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoutingTopologyMonitor']", 'unique': 'True', 'primary_key': 'True'})
        },
        'routing_olsr.olsrtopologylink': {
            'Meta': {'object_name': 'OlsrTopologyLink', '_ormbases': ['core.TopologyLink']},
            'etx': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'ilq': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'lq': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'topologylink_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyLink']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['routing_olsr']

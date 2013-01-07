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
        # Changing field 'RouterIdConfig.root'
        db.alter_column('core_routeridconfig', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'StatusMonitor.root'
        db.alter_column('core_statusmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'RoutingAnnounceMonitor.root'
        db.alter_column('core_routingannouncemonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'GeneralConfig.root'
        db.alter_column('core_generalconfig', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'RoutingTopologyMonitor.root'
        db.alter_column('core_routingtopologymonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'BasicAddressingConfig.root'
        db.alter_column('core_basicaddressingconfig', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'SystemStatusMonitor.root'
        db.alter_column('core_systemstatusmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'GeneralMonitor.root'
        db.alter_column('core_generalmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

        # Changing field 'TopologyLink.peer'
        db.alter_column('core_topologylink', 'peer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node']))

    def backwards(self, orm):
        # Changing field 'RouterIdConfig.root'
        db.alter_column('core_routeridconfig', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'StatusMonitor.root'
        db.alter_column('core_statusmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'RoutingAnnounceMonitor.root'
        db.alter_column('core_routingannouncemonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'GeneralConfig.root'
        db.alter_column('core_generalconfig', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'RoutingTopologyMonitor.root'
        db.alter_column('core_routingtopologymonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'BasicAddressingConfig.root'
        db.alter_column('core_basicaddressingconfig', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'SystemStatusMonitor.root'
        db.alter_column('core_systemstatusmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'GeneralMonitor.root'
        db.alter_column('core_generalmonitor', 'root_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

        # Changing field 'TopologyLink.peer'
        db.alter_column('core_topologylink', 'peer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node']))

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.basicaddressingconfig': {
            'Meta': {'object_name': 'BasicAddressingConfig'},
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'allocations_core_basicaddressingconfig'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['core.IpPool']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#ip_family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pool': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.IpPool']", 'on_delete': 'models.PROTECT'}),
            'prefix_length': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_basicaddressingconfig'", 'to': "orm['core.Node']"}),
            'subnet_hint': ('nodewatcher.core.registry.fields.IPAddressField', [], {'host_required': 'True', 'null': 'True', 'blank': 'True'})
        },
        'core.generalconfig': {
            'Meta': {'object_name': 'GeneralConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_generalconfig'", 'to': "orm['core.Node']"})
        },
        'core.generalmonitor': {
            'Meta': {'object_name': 'GeneralMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_generalmonitor'", 'to': "orm['core.Node']"})
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
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'core.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        },
        'core.routeridconfig': {
            'Meta': {'object_name': 'RouterIdConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.routerid#family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_routeridconfig'", 'to': "orm['core.Node']"}),
            'router_id': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.routingannouncemonitor': {
            'Meta': {'object_name': 'RoutingAnnounceMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'network': ('nodewatcher.core.registry.fields.IPAddressField', [], {}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_routingannouncemonitor'", 'to': "orm['core.Node']"}),
            'status': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.monitoring'", 'enum_id': "'network.routing.announces#status'"})
        },
        'core.routingtopologymonitor': {
            'Meta': {'object_name': 'RoutingTopologyMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_routingtopologymonitor'", 'to': "orm['core.Node']"})
        },
        'core.statusmonitor': {
            'Meta': {'object_name': 'StatusMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'has_warnings': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_statusmonitor'", 'to': "orm['core.Node']"}),
            'status': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.monitoring'", 'enum_id': "'core.status#status'"})
        },
        'core.systemstatusmonitor': {
            'Meta': {'object_name': 'SystemStatusMonitor'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_time': ('django.db.models.fields.DateTimeField', [], {}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'monitoring_core_systemstatusmonitor'", 'to': "orm['core.Node']"}),
            'uptime': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'core.topologylink': {
            'Meta': {'object_name': 'TopologyLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'monitor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['core.RoutingTopologyMonitor']"}),
            'peer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['core.Node']"}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_core.topologylink_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"})
        }
    }

    complete_apps = ['core']
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'RedundantNodeRoleConfig'
        db.create_table('core_redundantnoderoleconfig', (
            ('roleconfig_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.RoleConfig'], unique=True, primary_key=True)),
            ('redundancy_required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('core', ['RedundantNodeRoleConfig'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'RedundantNodeRoleConfig'
        db.delete_table('core_redundantnoderoleconfig')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.allocation': {
            'Meta': {'object_name': 'Allocation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Pool']"})
        },
        'core.basicaddressingconfig': {
            'Meta': {'object_name': 'BasicAddressingConfig'},
            'cidr': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pool': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Pool']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_basicaddressingconfig'", 'to': "orm['nodes.Node']"}),
            'usage': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'core.borderrouterroleconfig': {
            'Meta': {'object_name': 'BorderRouterRoleConfig', '_ormbases': ['core.RoleConfig']},
            'border_router': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoleConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.generalconfig': {
            'Meta': {'object_name': 'GeneralConfig'},
            'altitude': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'geolocation': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'project': ('web.registry.fields.ModelSelectorKeyField', [], {'to': "orm['nodes.Project']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_generalconfig'", 'to': "orm['nodes.Node']"}),
            'type': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#type'"}),
            'url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'core.pool': {
            'Meta': {'object_name': 'Pool'},
            'cidr': ('django.db.models.fields.IntegerField', [], {}),
            'default_prefix_len': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('web.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('django.db.models.fields.CharField', [], {'null': 'True'}),
            'max_prefix_len': ('django.db.models.fields.IntegerField', [], {'default': '28', 'null': 'True'}),
            'min_prefix_len': ('django.db.models.fields.IntegerField', [], {'default': '24', 'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['core.Pool']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'core.redundantnoderoleconfig': {
            'Meta': {'object_name': 'RedundantNodeRoleConfig', '_ormbases': ['core.RoleConfig']},
            'redundancy_required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoleConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.roleconfig': {
            'Meta': {'object_name': 'RoleConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_roleconfig'", 'to': "orm['nodes.Node']"})
        },
        'core.systemroleconfig': {
            'Meta': {'object_name': 'SystemRoleConfig', '_ormbases': ['core.RoleConfig']},
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoleConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'core.vpnserverroleconfig': {
            'Meta': {'object_name': 'VpnServerRoleConfig', '_ormbases': ['core.RoleConfig']},
            'roleconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.RoleConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'vpn_server': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'dns.zone': {
            'Meta': {'object_name': 'Zone'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'expire': ('django.db.models.fields.IntegerField', [], {}),
            'minimum': ('django.db.models.fields.IntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'primary_ns': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'refresh': ('django.db.models.fields.IntegerField', [], {}),
            'resp_person': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'retry': ('django.db.models.fields.IntegerField', [], {}),
            'serial': ('django.db.models.fields.IntegerField', [], {}),
            'zone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'nodes.link': {
            'Meta': {'object_name': 'Link'},
            'dst': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dst'", 'to': "orm['nodes.Node']"}),
            'etx': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ilq': ('django.db.models.fields.FloatField', [], {}),
            'lq': ('django.db.models.fields.FloatField', [], {}),
            'src': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'src'", 'to': "orm['nodes.Node']"}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'vtime': ('django.db.models.fields.FloatField', [], {})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'ant_external': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'ant_polarization': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ant_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'awaiting_renumber': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'border_router': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'bssid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'captive_portal_status': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'channel': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'clients': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'clients_so_far': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'conflicting_subnets': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'dns_works': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'firmware_version': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'first_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'geo_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'geo_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'loadavg_15min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'loadavg_1min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'loadavg_5min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'local_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'loss_count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'memfree': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True', 'null': 'True'}),
            'node_type': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'notes': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'numproc': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'peer_history': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'peer_history_rel_+'", 'to': "orm['nodes.Node']"}),
            'peer_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['nodes.Node']", 'through': "orm['nodes.Link']", 'symmetrical': 'False'}),
            'peers': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'pkt_loss': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nodes'", 'null': 'True', 'to': "orm['nodes.Project']"}),
            'redundancy_link': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'redundancy_req': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'reported_uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'rtt_avg': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_max': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'system_node': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'thresh_frag': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'thresh_rts': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'uptime': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'uptime_last': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'uptime_so_far': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'vpn_mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'vpn_mac_conf': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True'}),
            'vpn_server': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'warnings': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'wifi_error_count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'wifi_mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'nodes.project': {
            'Meta': {'object_name': 'Project'},
            'captive_portal': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'channel': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'geo_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'geo_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'geo_zoom': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Pool']"}),
            'pools': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['core.Pool']"}),
            'ssid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ssid_backbone': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ssid_mobile': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sticker': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dns.Zone']", 'null': 'True'})
        }
    }
    
    complete_apps = ['core']

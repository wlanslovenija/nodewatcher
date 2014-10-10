# encoding: utf-8
from django.utils import timezone
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    depends_on = (
        ("guardian", "0005_auto__chg_field_groupobjectpermission_object_pk__chg_field_userobjectp"),
    )

    def forwards(self, orm):
        names = {
            'reset_node': 'Can reset node',
            'generate_firmware': 'Can generate firmware',
        }

        # Assign change and remove permissions to node maintainers
        for node in orm['nodes.Node'].objects.filter(owner__isnull = False):
            for perm in ('change_node', 'delete_node', 'reset_node', 'generate_firmware'):
                content_type = orm['contenttypes.ContentType'].objects.get(app_label = 'nodes', model = 'node')
                if perm in ('reset_node', 'generate_firmware'):
                    permission, created = orm['auth.Permission'].objects.get_or_create(
                        content_type=content_type,
                        codename=perm,
                        name=names[perm],
                    )
                else:
                    permission = orm['auth.Permission'].objects.get(content_type = content_type, codename = perm)

                orm['guardian.UserObjectPermission'].objects.get_or_create(
                    content_type = content_type,
                    permission = permission,
                    object_pk = node.pk,
                    user = node.owner
                )

    def backwards(self, orm):
        # Remove all user object permissions for nodes
        content_type = orm['contenttypes.ContentType'].objects.get(app_label = 'nodes', model = 'node')
        orm['guardian.UserObjectPermission'].objects.filter(content_type = content_type).delete()

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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
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
        'core.pool': {
            'Meta': {'object_name': 'Pool'},
            'cidr': ('django.db.models.fields.IntegerField', [], {}),
            'default_prefix_len': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('django.db.models.fields.CharField', [], {'null': 'True'}),
            'max_prefix_len': ('django.db.models.fields.IntegerField', [], {'default': '28', 'null': 'True'}),
            'min_prefix_len': ('django.db.models.fields.IntegerField', [], {'default': '24', 'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['core.Pool']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
        'guardian.groupobjectpermission': {
            'Meta': {'unique_together': "(['group', 'permission', 'content_type', 'object_pk'],)", 'object_name': 'GroupObjectPermission'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Permission']"})
        },
        'guardian.userobjectpermission': {
            'Meta': {'unique_together': "(['user', 'permission', 'content_type', 'object_pk'],)", 'object_name': 'UserObjectPermission'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Permission']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'nodes.apclient': {
            'Meta': {'object_name': 'APClient'},
            'connected_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'downloaded': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'uploaded': ('django.db.models.fields.IntegerField', [], {})
        },
        'nodes.event': {
            'Meta': {'object_name': 'Event'},
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'counter': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need_resend': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'source': ('django.db.models.fields.IntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'nodes.eventsubscription': {
            'Meta': {'object_name': 'EventSubscription'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']", 'null': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'nodes.graphitem': {
            'Meta': {'object_name': 'GraphItem'},
            'dead': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'display_priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'graph': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'need_redraw': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'need_removal': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['nodes.GraphItem']"}),
            'rra': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'nodes.installedpackage': {
            'Meta': {'object_name': 'InstalledPackage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        'nodes.nodenames': {
            'Meta': {'object_name': 'NodeNames'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'names'", 'to': "orm['nodes.Node']"})
        },
        'nodes.nodewarning': {
            'Meta': {'object_name': 'NodeWarning'},
            'code': ('django.db.models.fields.IntegerField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'details': ('django.db.models.fields.TextField', [], {}),
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'warning_list'", 'to': "orm['nodes.Node']"}),
            'source': ('django.db.models.fields.IntegerField', [], {})
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
        },
        'nodes.renumbernotice': {
            'Meta': {'object_name': 'RenumberNotice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'renumber_notices'", 'unique': 'True', 'to': "orm['nodes.Node']"}),
            'original_ip': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'renumbered_at': ('django.db.models.fields.DateTimeField', [], {})
        },
        'nodes.statssolar': {
            'Meta': {'object_name': 'StatsSolar'},
            'batvoltage': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'charge': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'solvoltage': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'nodes.subnet': {
            'Meta': {'object_name': 'Subnet'},
            'allocated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allocated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'cidr': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'gen_dhcp': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'gen_iface_type': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('django.db.models.fields.CharField', [], {'null': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'subnet': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'})
        },
        'nodes.tweet': {
            'Meta': {'object_name': 'Tweet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tweets'", 'to': "orm['nodes.Node']"}),
            'tweet_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'nodes.whitelistitem': {
            'Meta': {'object_name': 'WhitelistItem'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'registred_at': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['guardian', 'nodes']

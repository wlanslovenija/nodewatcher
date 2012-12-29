# encoding: utf-8
from django.utils import timezone
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting field 'Node.bssid'
        db.delete_column('nodes_node', 'bssid')

        # Deleting field 'Node.conflicting_subnets'
        db.delete_column('nodes_node', 'conflicting_subnets')

        # Deleting field 'Node.loadavg_1min'
        db.delete_column('nodes_node', 'loadavg_1min')

        # Deleting field 'Node.visible'
        db.delete_column('nodes_node', 'visible')

        # Deleting field 'Node.owner'
        db.delete_column('nodes_node', 'owner_id')

        # Deleting field 'Node.first_seen'
        db.delete_column('nodes_node', 'first_seen')

        # Deleting field 'Node.wifi_error_count'
        db.delete_column('nodes_node', 'wifi_error_count')

        # Deleting field 'Node.thresh_frag'
        db.delete_column('nodes_node', 'thresh_frag')

        # Deleting field 'Node.rtt_min'
        db.delete_column('nodes_node', 'rtt_min')

        # Deleting field 'Node.geo_lat'
        db.delete_column('nodes_node', 'geo_lat')

        # Deleting field 'Node.ant_external'
        db.delete_column('nodes_node', 'ant_external')

        # Deleting field 'Node.location'
        db.delete_column('nodes_node', 'location')

        # Deleting field 'Node.pkt_loss'
        db.delete_column('nodes_node', 'pkt_loss')

        # Deleting field 'Node.reported_uuid'
        db.delete_column('nodes_node', 'reported_uuid')

        # Deleting field 'Node.vpn_mac_conf'
        db.delete_column('nodes_node', 'vpn_mac_conf')

        # Deleting field 'Node.memfree'
        db.delete_column('nodes_node', 'memfree')

        # Deleting field 'Node.rtt_max'
        db.delete_column('nodes_node', 'rtt_max')

        # Deleting field 'Node.redundancy_link'
        db.delete_column('nodes_node', 'redundancy_link')

        # Deleting field 'Node.uptime_last'
        db.delete_column('nodes_node', 'uptime_last')

        # Deleting field 'Node.name'
        db.delete_column('nodes_node', 'name')

        # Deleting field 'Node.notes'
        db.delete_column('nodes_node', 'notes')

        # Deleting field 'Node.clients'
        db.delete_column('nodes_node', 'clients')

        # Deleting field 'Node.vpn_mac'
        db.delete_column('nodes_node', 'vpn_mac')

        # Deleting field 'Node.project'
        db.delete_column('nodes_node', 'project_id')

        # Deleting field 'Node.loadavg_15min'
        db.delete_column('nodes_node', 'loadavg_15min')

        # Deleting field 'Node.dns_works'
        db.delete_column('nodes_node', 'dns_works')

        # Deleting field 'Node.loss_count'
        db.delete_column('nodes_node', 'loss_count')

        # Deleting field 'Node.ant_polarization'
        db.delete_column('nodes_node', 'ant_polarization')

        # Deleting field 'Node.ip'
        db.delete_column('nodes_node', 'ip')

        # Deleting field 'Node.awaiting_renumber'
        db.delete_column('nodes_node', 'awaiting_renumber')

        # Deleting field 'Node.node_type'
        db.delete_column('nodes_node', 'node_type')

        # Deleting field 'Node.firmware_version'
        db.delete_column('nodes_node', 'firmware_version')

        # Deleting field 'Node.uptime'
        db.delete_column('nodes_node', 'uptime')

        # Deleting field 'Node.captive_portal_status'
        db.delete_column('nodes_node', 'captive_portal_status')

        # Deleting field 'Node.geo_long'
        db.delete_column('nodes_node', 'geo_long')

        # Deleting field 'Node.wifi_mac'
        db.delete_column('nodes_node', 'wifi_mac')

        # Deleting field 'Node.channel'
        db.delete_column('nodes_node', 'channel')

        # Deleting field 'Node.essid'
        db.delete_column('nodes_node', 'essid')

        # Deleting field 'Node.status'
        db.delete_column('nodes_node', 'status')

        # Deleting field 'Node.redundancy_req'
        db.delete_column('nodes_node', 'redundancy_req')

        # Deleting field 'Node.loadavg_5min'
        db.delete_column('nodes_node', 'loadavg_5min')

        # Deleting field 'Node.warnings'
        db.delete_column('nodes_node', 'warnings')

        # Deleting field 'Node.rtt_avg'
        db.delete_column('nodes_node', 'rtt_avg')

        # Deleting field 'Node.border_router'
        db.delete_column('nodes_node', 'border_router')

        # Deleting field 'Node.system_node'
        db.delete_column('nodes_node', 'system_node')

        # Deleting field 'Node.numproc'
        db.delete_column('nodes_node', 'numproc')

        # Deleting field 'Node.clients_so_far'
        db.delete_column('nodes_node', 'clients_so_far')

        # Deleting field 'Node.peers'
        db.delete_column('nodes_node', 'peers')

        # Deleting field 'Node.url'
        db.delete_column('nodes_node', 'url')

        # Deleting field 'Node.uptime_so_far'
        db.delete_column('nodes_node', 'uptime_so_far')

        # Deleting field 'Node.thresh_rts'
        db.delete_column('nodes_node', 'thresh_rts')

        # Deleting field 'Node.local_time'
        db.delete_column('nodes_node', 'local_time')

        # Deleting field 'Node.last_seen'
        db.delete_column('nodes_node', 'last_seen')

        # Deleting field 'Node.vpn_server'
        db.delete_column('nodes_node', 'vpn_server')

        # Deleting field 'Node.ant_type'
        db.delete_column('nodes_node', 'ant_type')

        # Removing M2M table for field peer_history on 'Node'
        db.delete_table('nodes_node_peer_history')


    def backwards(self, orm):

        # Adding field 'Node.bssid'
        db.add_column('nodes_node', 'bssid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True), keep_default=False)

        # Adding field 'Node.conflicting_subnets'
        db.add_column('nodes_node', 'conflicting_subnets', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.loadavg_1min'
        db.add_column('nodes_node', 'loadavg_1min', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'Node.visible'
        db.add_column('nodes_node', 'visible', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.owner'
        db.add_column('nodes_node', 'owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True), keep_default=False)

        # Adding field 'Node.first_seen'
        db.add_column('nodes_node', 'first_seen', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding field 'Node.wifi_error_count'
        db.add_column('nodes_node', 'wifi_error_count', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.thresh_frag'
        db.add_column('nodes_node', 'thresh_frag', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.rtt_min'
        db.add_column('nodes_node', 'rtt_min', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'Node.geo_lat'
        db.add_column('nodes_node', 'geo_lat', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'Node.ant_external'
        db.add_column('nodes_node', 'ant_external', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.location'
        db.add_column('nodes_node', 'location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True), keep_default=False)

        # Adding field 'Node.pkt_loss'
        db.add_column('nodes_node', 'pkt_loss', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.reported_uuid'
        db.add_column('nodes_node', 'reported_uuid', self.gf('django.db.models.fields.CharField')(max_length=40, null=True), keep_default=False)

        # Adding field 'Node.vpn_mac_conf'
        db.add_column('nodes_node', 'vpn_mac_conf', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20, null=True), keep_default=False)

        # Adding field 'Node.memfree'
        db.add_column('nodes_node', 'memfree', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.rtt_max'
        db.add_column('nodes_node', 'rtt_max', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'Node.redundancy_link'
        db.add_column('nodes_node', 'redundancy_link', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.uptime_last'
        db.add_column('nodes_node', 'uptime_last', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding field 'Node.name'
        db.add_column('nodes_node', 'name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, null=True), keep_default=False)

        # Adding field 'Node.notes'
        db.add_column('nodes_node', 'notes', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True), keep_default=False)

        # Adding field 'Node.clients'
        db.add_column('nodes_node', 'clients', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.vpn_mac'
        db.add_column('nodes_node', 'vpn_mac', self.gf('django.db.models.fields.CharField')(max_length=20, null=True), keep_default=False)

        # Adding field 'Node.project'
        db.add_column('nodes_node', 'project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nodes', null=True, to=orm['nodes.Project']), keep_default=False)

        # Adding field 'Node.loadavg_15min'
        db.add_column('nodes_node', 'loadavg_15min', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'Node.dns_works'
        db.add_column('nodes_node', 'dns_works', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'Node.loss_count'
        db.add_column('nodes_node', 'loss_count', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.ant_polarization'
        db.add_column('nodes_node', 'ant_polarization', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'Node.ip'
        raise RuntimeError("Cannot reverse this migration. 'Node.ip' and its values cannot be restored.")

        # Adding field 'Node.awaiting_renumber'
        db.add_column('nodes_node', 'awaiting_renumber', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.node_type'
        db.add_column('nodes_node', 'node_type', self.gf('django.db.models.fields.IntegerField')(default=2), keep_default=False)

        # Adding field 'Node.firmware_version'
        db.add_column('nodes_node', 'firmware_version', self.gf('django.db.models.fields.CharField')(max_length=50, null=True), keep_default=False)

        # Adding field 'Node.uptime'
        db.add_column('nodes_node', 'uptime', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.captive_portal_status'
        db.add_column('nodes_node', 'captive_portal_status', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'Node.geo_long'
        db.add_column('nodes_node', 'geo_long', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'Node.wifi_mac'
        db.add_column('nodes_node', 'wifi_mac', self.gf('django.db.models.fields.CharField')(max_length=20, null=True), keep_default=False)

        # Adding field 'Node.channel'
        db.add_column('nodes_node', 'channel', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.essid'
        db.add_column('nodes_node', 'essid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True), keep_default=False)

        # Adding field 'Node.status'
        db.add_column('nodes_node', 'status', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.redundancy_req'
        db.add_column('nodes_node', 'redundancy_req', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.loadavg_5min'
        db.add_column('nodes_node', 'loadavg_5min', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'Node.warnings'
        db.add_column('nodes_node', 'warnings', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.rtt_avg'
        db.add_column('nodes_node', 'rtt_avg', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'Node.border_router'
        db.add_column('nodes_node', 'border_router', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.system_node'
        db.add_column('nodes_node', 'system_node', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.numproc'
        db.add_column('nodes_node', 'numproc', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.clients_so_far'
        db.add_column('nodes_node', 'clients_so_far', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'Node.peers'
        db.add_column('nodes_node', 'peers', self.gf('django.db.models.fields.IntegerField')(default=0, null=True), keep_default=False)

        # Adding field 'Node.url'
        db.add_column('nodes_node', 'url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True), keep_default=False)

        # Adding field 'Node.uptime_so_far'
        db.add_column('nodes_node', 'uptime_so_far', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.thresh_rts'
        db.add_column('nodes_node', 'thresh_rts', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Node.local_time'
        db.add_column('nodes_node', 'local_time', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding field 'Node.last_seen'
        db.add_column('nodes_node', 'last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)

        # Adding field 'Node.vpn_server'
        db.add_column('nodes_node', 'vpn_server', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Node.ant_type'
        db.add_column('nodes_node', 'ant_type', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding M2M table for field peer_history on 'Node'
        db.create_table('nodes_node_peer_history', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_node', models.ForeignKey(orm['nodes.node'], null=False)),
            ('to_node', models.ForeignKey(orm['nodes.node'], null=False))
        ))
        db.create_unique('nodes_node_peer_history', ['from_node_id', 'to_node_id'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dns.zone': {
            'Meta': {'object_name': 'Zone'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'need_resend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'source': ('django.db.models.fields.IntegerField', [], {}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'nodes.eventsubscription': {
            'Meta': {'object_name': 'EventSubscription'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']", 'null': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'nodes.graphitem': {
            'Meta': {'object_name': 'GraphItem'},
            'dead': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'display_priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'graph': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'need_redraw': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'need_removal': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
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
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'vtime': ('django.db.models.fields.FloatField', [], {})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
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
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'warning_list'", 'to': "orm['nodes.Node']"}),
            'source': ('django.db.models.fields.IntegerField', [], {})
        },
        'nodes.project': {
            'Meta': {'object_name': 'Project'},
            'captive_portal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'channel': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'geo_lat': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'geo_long': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'geo_zoom': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'allocated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allocated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'cidr': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'gen_dhcp': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'gen_iface_type': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('django.db.models.fields.CharField', [], {'null': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Node']"}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'subnet': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
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

    complete_apps = ['nodes']

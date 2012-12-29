# encoding: utf-8
from django.utils import timezone
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Project'
        db.create_table('nodes_project', (
            ('ssid_mobile', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ssid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dns.Zone'], null=True)),
            ('captive_portal', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('sticker', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('geo_lat', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('pool', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Pool'])),
            ('geo_long', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('ssid_backbone', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('geo_zoom', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('nodes', ['Project'])

        # Adding M2M table for field pools on 'Project'
        db.create_table('nodes_project_pools', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['nodes.project'], null=False)),
            ('pool', models.ForeignKey(orm['nodes.pool'], null=False))
        ))
        db.create_unique('nodes_project_pools', ['project_id', 'pool_id'])

        # Adding model 'Node'
        db.create_table('nodes_node', (
            ('reported_uuid', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('ant_polarization', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ip', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('conflicting_subnets', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('awaiting_renumber', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('loadavg_1min', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('node_type', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('first_seen', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('firmware_version', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('uptime', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('numproc', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('wifi_error_count', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=40, primary_key=True)),
            ('rtt_min', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('captive_portal_status', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('geo_lat', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('ant_external', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('bssid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('geo_long', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('wifi_mac', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('pkt_loss', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('channel', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('local_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('redundancy_req', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('loadavg_5min', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('warnings', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('rtt_avg', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('border_router', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('vpn_mac_conf', self.gf('django.db.models.fields.CharField')(max_length=20, unique=True, null=True)),
            ('memfree', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('rtt_max', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('system_node', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('redundancy_link', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('clients_so_far', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('peers', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('uptime_last', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True, null=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('notes', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
            ('clients', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('vpn_mac', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='nodes', null=True, to=orm['nodes.Project'])),
            ('thresh_rts', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('essid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('loadavg_15min', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('dns_works', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('thresh_frag', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('loss_count', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('vpn_server', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('uptime_so_far', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('ant_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('nodes', ['Node'])

        # Adding M2M table for field peer_history on 'Node'
        db.create_table('nodes_node_peer_history', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_node', models.ForeignKey(orm['nodes.node'], null=False)),
            ('to_node', models.ForeignKey(orm['nodes.node'], null=False))
        ))
        db.create_unique('nodes_node_peer_history', ['from_node_id', 'to_node_id'])

        # Adding model 'Link'
        db.create_table('nodes_link', (
            ('src', self.gf('django.db.models.fields.related.ForeignKey')(related_name='src', to=orm['nodes.Node'])),
            ('vtime', self.gf('django.db.models.fields.FloatField')()),
            ('etx', self.gf('django.db.models.fields.FloatField')()),
            ('lq', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('ilq', self.gf('django.db.models.fields.FloatField')()),
            ('dst', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dst', to=orm['nodes.Node'])),
        ))
        db.send_create_signal('nodes', ['Link'])

        # Adding model 'Subnet'
        db.create_table('nodes_subnet', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('subnet', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('allocated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('ip_subnet', self.gf('django.db.models.fields.CharField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gen_dhcp', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('gen_iface_type', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('cidr', self.gf('django.db.models.fields.IntegerField')()),
            ('allocated', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('nodes', ['Subnet'])

        # Adding model 'RenumberNotice'
        db.create_table('nodes_renumbernotice', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='renumber_notices', unique=True, to=orm['nodes.Node'])),
            ('original_ip', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('renumbered_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['RenumberNotice'])

        # Adding model 'APClient'
        db.create_table('nodes_apclient', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('uploaded', self.gf('django.db.models.fields.IntegerField')()),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('downloaded', self.gf('django.db.models.fields.IntegerField')()),
            ('connected_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['APClient'])

        # Adding model 'GraphItem'
        db.create_table('nodes_graphitem', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['nodes.GraphItem'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('display_priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('graph', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('need_removal', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('rra', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('dead', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('need_redraw', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['GraphItem'])

        # Adding model 'WhitelistItem'
        db.create_table('nodes_whitelistitem', (
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registred_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('nodes', ['WhitelistItem'])

        # Adding model 'Pool'
        db.create_table('nodes_pool', (
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('min_prefix_len', self.gf('django.db.models.fields.IntegerField')(default=24, null=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['nodes.Pool'])),
            ('family', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('default_prefix_len', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('max_prefix_len', self.gf('django.db.models.fields.IntegerField')(default=28, null=True)),
            ('ip_subnet', self.gf('django.db.models.fields.CharField')(null=True)),
            ('cidr', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('nodes', ['Pool'])

        # Adding model 'StatsSolar'
        db.create_table('nodes_statssolar', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('load', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('batvoltage', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('charge', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('solvoltage', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['StatsSolar'])

        # Adding model 'Event'
        db.create_table('nodes_event', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('counter', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('source', self.gf('django.db.models.fields.IntegerField')()),
            ('need_resend', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['Event'])

        # Adding model 'EventSubscription'
        db.create_table('nodes_eventsubscription', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'], null=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['EventSubscription'])

        # Adding model 'NodeWarning'
        db.create_table('nodes_nodewarning', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='warning_list', to=orm['nodes.Node'])),
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('source', self.gf('django.db.models.fields.IntegerField')()),
            ('details', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dirty', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('nodes', ['NodeWarning'])

        # Adding model 'InstalledPackage'
        db.create_table('nodes_installedpackage', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('nodes', ['InstalledPackage'])

        # Adding model 'Tweet'
        db.create_table('nodes_tweet', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tweets', to=orm['nodes.Node'])),
            ('tweet_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['Tweet'])

        # Adding model 'NodeNames'
        db.create_table('nodes_nodenames', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='names', to=orm['nodes.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['NodeNames'])


    def backwards(self, orm):

        # Deleting model 'Project'
        db.delete_table('nodes_project')

        # Removing M2M table for field pools on 'Project'
        db.delete_table('nodes_project_pools')

        # Deleting model 'Node'
        db.delete_table('nodes_node')

        # Removing M2M table for field peer_history on 'Node'
        db.delete_table('nodes_node_peer_history')

        # Deleting model 'Link'
        db.delete_table('nodes_link')

        # Deleting model 'Subnet'
        db.delete_table('nodes_subnet')

        # Deleting model 'RenumberNotice'
        db.delete_table('nodes_renumbernotice')

        # Deleting model 'APClient'
        db.delete_table('nodes_apclient')

        # Deleting model 'GraphItem'
        db.delete_table('nodes_graphitem')

        # Deleting model 'WhitelistItem'
        db.delete_table('nodes_whitelistitem')

        # Deleting model 'Pool'
        db.delete_table('nodes_pool')

        # Deleting model 'StatsSolar'
        db.delete_table('nodes_statssolar')

        # Deleting model 'Event'
        db.delete_table('nodes_event')

        # Deleting model 'EventSubscription'
        db.delete_table('nodes_eventsubscription')

        # Deleting model 'NodeWarning'
        db.delete_table('nodes_nodewarning')

        # Deleting model 'InstalledPackage'
        db.delete_table('nodes_installedpackage')

        # Deleting model 'Tweet'
        db.delete_table('nodes_tweet')

        # Deleting model 'NodeNames'
        db.delete_table('nodes_nodenames')


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
        'nodes.pool': {
            'Meta': {'object_name': 'Pool'},
            'cidr': ('django.db.models.fields.IntegerField', [], {}),
            'default_prefix_len': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_subnet': ('django.db.models.fields.CharField', [], {'null': 'True'}),
            'max_prefix_len': ('django.db.models.fields.IntegerField', [], {'default': '28', 'null': 'True'}),
            'min_prefix_len': ('django.db.models.fields.IntegerField', [], {'default': '24', 'null': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['nodes.Pool']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['nodes.Pool']"}),
            'pools': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['nodes.Pool']"}),
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

    complete_apps = ['nodes']

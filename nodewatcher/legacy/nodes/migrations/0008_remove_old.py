# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'NodeWarning'
        db.delete_table('nodes_nodewarning')

        # Deleting model 'StatsSolar'
        db.delete_table('nodes_statssolar')

        # Deleting model 'WhitelistItem'
        db.delete_table('nodes_whitelistitem')

        # Deleting model 'EventSubscription'
        db.delete_table('nodes_eventsubscription')

        # Deleting model 'NodeNames'
        db.delete_table('nodes_nodenames')

        # Deleting model 'RenumberNotice'
        db.delete_table('nodes_renumbernotice')

        # Deleting model 'Subnet'
        db.delete_table('nodes_subnet')

        # Deleting model 'Event'
        db.delete_table('nodes_event')

        # Deleting model 'Tweet'
        db.delete_table('nodes_tweet')

        # Deleting model 'InstalledPackage'
        db.delete_table('nodes_installedpackage')

        # Deleting model 'GraphItem'
        db.delete_table('nodes_graphitem')

        # Deleting model 'APClient'
        db.delete_table('nodes_apclient')

        # Deleting model 'Link'
        db.delete_table('nodes_link')

    def backwards(self, orm):
        # Adding model 'NodeWarning'
        db.create_table('nodes_nodewarning', (
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='warning_list', to=orm['nodes.Node'])),
            ('details', self.gf('django.db.models.fields.TextField')()),
            ('source', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dirty', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('nodes', ['NodeWarning'])

        # Adding model 'StatsSolar'
        db.create_table('nodes_statssolar', (
            ('load', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('batvoltage', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('solvoltage', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('charge', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['StatsSolar'])

        # Adding model 'WhitelistItem'
        db.create_table('nodes_whitelistitem', (
            ('registred_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('mac', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
        ))
        db.send_create_signal('nodes', ['WhitelistItem'])

        # Adding model 'EventSubscription'
        db.create_table('nodes_eventsubscription', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'], null=True)),
            ('code', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['EventSubscription'])

        # Adding model 'NodeNames'
        db.create_table('nodes_nodenames', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='names', to=orm['nodes.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
        ))
        db.send_create_signal('nodes', ['NodeNames'])

        # Adding model 'RenumberNotice'
        db.create_table('nodes_renumbernotice', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='renumber_notices', unique=True, to=orm['nodes.Node'])),
            ('original_ip', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('renumbered_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['RenumberNotice'])

        # Adding model 'Subnet'
        db.create_table('nodes_subnet', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('allocated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('ip_subnet', self.gf('django.db.models.fields.CharField')(null=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('allocated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cidr', self.gf('django.db.models.fields.IntegerField')()),
            ('subnet', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gen_dhcp', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('gen_iface_type', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('nodes', ['Subnet'])

        # Adding model 'Event'
        db.create_table('nodes_event', (
            ('code', self.gf('django.db.models.fields.IntegerField')()),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('need_resend', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('source', self.gf('django.db.models.fields.IntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('counter', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('summary', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('nodes', ['Event'])

        # Adding model 'Tweet'
        db.create_table('nodes_tweet', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tweets', to=orm['nodes.Node'])),
            ('tweet_id', self.gf('django.db.models.fields.CharField')(max_length=50, unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['Tweet'])

        # Adding model 'InstalledPackage'
        db.create_table('nodes_installedpackage', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['InstalledPackage'])

        # Adding model 'GraphItem'
        db.create_table('nodes_graphitem', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', null=True, to=orm['nodes.GraphItem'])),
            ('display_priority', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('need_removal', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('dead', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('rra', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('need_redraw', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('graph', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('nodes', ['GraphItem'])

        # Adding model 'APClient'
        db.create_table('nodes_apclient', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nodes.Node'])),
            ('downloaded', self.gf('django.db.models.fields.IntegerField')()),
            ('connected_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('uploaded', self.gf('django.db.models.fields.IntegerField')()),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('nodes', ['APClient'])

        # Adding model 'Link'
        db.create_table('nodes_link', (
            ('src', self.gf('django.db.models.fields.related.ForeignKey')(related_name='src', to=orm['nodes.Node'])),
            ('vtime', self.gf('django.db.models.fields.FloatField')()),
            ('ilq', self.gf('django.db.models.fields.FloatField')()),
            ('dst', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dst', to=orm['nodes.Node'])),
            ('lq', self.gf('django.db.models.fields.FloatField')()),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('etx', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('nodes', ['Link'])

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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
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
        }
    }

    complete_apps = ['nodes']

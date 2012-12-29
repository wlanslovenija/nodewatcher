# encoding: utf-8
from django.utils import timezone
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'ImageFile'
        db.create_table('generator_imagefile', (
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('generator', ['ImageFile'])

        # Adding model 'Template'
        db.create_table('generator_template', (
            ('iface_wifi', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('iface_lan', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('driver', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('port_layout', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('openwrt_version', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('iface_wan', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('channel', self.gf('django.db.models.fields.IntegerField')()),
            ('imagebuilder', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('arch', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('experimental', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('generator', ['Template'])

        # Adding M2M table for field imagefiles on 'Template'
        db.create_table('generator_template_imagefiles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('template', models.ForeignKey(orm['generator.template'], null=False)),
            ('imagefile', models.ForeignKey(orm['generator.imagefile'], null=False))
        ))
        db.create_unique('generator_template_imagefiles', ['template_id', 'imagefile_id'])

        # Adding model 'IfaceTemplate'
        db.create_table('generator_ifacetemplate', (
            ('ifname', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Template'])),
        ))
        db.send_create_signal('generator', ['IfaceTemplate'])

        # Adding model 'OptionalPackage'
        db.create_table('generator_optionalpackage', (
            ('fancy_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('generator', ['OptionalPackage'])

        # Adding model 'ProjectPackage'
        db.create_table('generator_projectpackage', (
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='packages', to=orm['nodes.Project'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('generator', ['ProjectPackage'])

        # Adding model 'ProfileAdaptationChain'
        db.create_table('generator_profileadaptationchain', (
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('class_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='adaptation_chain', to=orm['generator.Template'])),
        ))
        db.send_create_signal('generator', ['ProfileAdaptationChain'])

        # Adding model 'Profile'
        db.create_table('generator_profile', (
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('root_pass', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('antenna', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('vpn_egress_limit', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('use_vpn', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('wan_ip', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('lan_bridge', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('wan_gw', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Template'])),
            ('wan_dhcp', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.IntegerField')()),
            ('wan_cidr', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('generator', ['Profile'])

        # Adding M2M table for field optional_packages on 'Profile'
        db.create_table('generator_profile_optional_packages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm['generator.profile'], null=False)),
            ('optionalpackage', models.ForeignKey(orm['generator.optionalpackage'], null=False))
        ))
        db.create_unique('generator_profile_optional_packages', ['profile_id', 'optionalpackage_id'])


    def backwards(self, orm):

        # Deleting model 'ImageFile'
        db.delete_table('generator_imagefile')

        # Deleting model 'Template'
        db.delete_table('generator_template')

        # Removing M2M table for field imagefiles on 'Template'
        db.delete_table('generator_template_imagefiles')

        # Deleting model 'IfaceTemplate'
        db.delete_table('generator_ifacetemplate')

        # Deleting model 'OptionalPackage'
        db.delete_table('generator_optionalpackage')

        # Deleting model 'ProjectPackage'
        db.delete_table('generator_projectpackage')

        # Deleting model 'ProfileAdaptationChain'
        db.delete_table('generator_profileadaptationchain')

        # Deleting model 'Profile'
        db.delete_table('generator_profile')

        # Removing M2M table for field optional_packages on 'Profile'
        db.delete_table('generator_profile_optional_packages')


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
        'generator.ifacetemplate': {
            'Meta': {'object_name': 'IfaceTemplate'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ifname': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['generator.Template']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'generator.imagefile': {
            'Meta': {'object_name': 'ImageFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'generator.optionalpackage': {
            'Meta': {'object_name': 'OptionalPackage'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'fancy_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'generator.profile': {
            'Meta': {'object_name': 'Profile'},
            'antenna': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'channel': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lan_bridge': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['nodes.Node']", 'unique': 'True'}),
            'optional_packages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['generator.OptionalPackage']", 'symmetrical': 'False'}),
            'root_pass': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['generator.Template']"}),
            'use_vpn': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'vpn_egress_limit': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'wan_cidr': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'wan_dhcp': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'wan_gw': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'wan_ip': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'})
        },
        'generator.profileadaptationchain': {
            'Meta': {'object_name': 'ProfileAdaptationChain'},
            'class_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adaptation_chain'", 'to': "orm['generator.Template']"})
        },
        'generator.projectpackage': {
            'Meta': {'object_name': 'ProjectPackage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'packages'", 'to': "orm['nodes.Project']"})
        },
        'generator.template': {
            'Meta': {'object_name': 'Template'},
            'arch': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'channel': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'driver': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'experimental': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iface_lan': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'iface_wan': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'iface_wifi': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'imagebuilder': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'imagefiles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['generator.ImageFile']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'openwrt_version': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'port_layout': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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

    complete_apps = ['generator']

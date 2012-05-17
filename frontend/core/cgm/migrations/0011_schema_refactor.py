# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('cgm_cgmpackageconfig', 'cgm_packageconfig')
        db.rename_table('cgm_cgminterfaceconfig', 'cgm_interfaceconfig')
        db.rename_table('cgm_cgmnetworkconfig', 'cgm_networkconfig')

        db.rename_column('cgm_vpninterfaceconfig', 'cgminterfaceconfig_ptr_id', 'interfaceconfig_ptr_id')
        db.rename_column('cgm_wifiinterfaceconfig', 'cgminterfaceconfig_ptr_id', 'interfaceconfig_ptr_id')
        db.rename_column('cgm_ethernetinterfaceconfig', 'cgminterfaceconfig_ptr_id', 'interfaceconfig_ptr_id')

        db.rename_column('cgm_dhcpnetworkconfig', 'cgmnetworkconfig_ptr_id', 'networkconfig_ptr_id')
        db.rename_column('cgm_staticnetworkconfig', 'cgmnetworkconfig_ptr_id', 'networkconfig_ptr_id')
        db.rename_column('cgm_allocatednetworkconfig', 'cgmnetworkconfig_ptr_id', 'networkconfig_ptr_id')
        db.rename_column('cgm_wifinetworkconfig', 'cgmnetworkconfig_ptr_id', 'networkconfig_ptr_id')
        db.rename_column('cgm_pppoenetworkconfig', 'cgmnetworkconfig_ptr_id', 'networkconfig_ptr_id')

    def backwards(self, orm):
        db.rename_table('cgm_packageconfig', 'cgm_cgmpackageconfig')
        db.rename_table('cgm_interfaceconfig', 'cgm_cgminterfaceconfig')
        db.rename_table('cgm_networkconfig', 'cgm_cgmnetworkconfig')

        db.rename_column('cgm_vpninterfaceconfig', 'interfaceconfig_ptr_id', 'cgminterfaceconfig_ptr_id')
        db.rename_column('cgm_wifiinterfaceconfig', 'interfaceconfig_ptr_id', 'cgminterfaceconfig_ptr_id')
        db.rename_column('cgm_ethernetinterfaceconfig', 'interfaceconfig_ptr_id', 'cgminterfaceconfig_ptr_id')

        db.rename_column('cgm_dhcpnetworkconfig', 'networkconfig_ptr_id', 'cgmnetworkconfig_ptr_id')
        db.rename_column('cgm_staticnetworkconfig', 'networkconfig_ptr_id', 'cgmnetworkconfig_ptr_id')
        db.rename_column('cgm_allocatednetworkconfig', 'networkconfig_ptr_id', 'cgmnetworkconfig_ptr_id')
        db.rename_column('cgm_wifinetworkconfig', 'networkconfig_ptr_id', 'cgmnetworkconfig_ptr_id')
        db.rename_column('cgm_pppoenetworkconfig', 'networkconfig_ptr_id', 'cgmnetworkconfig_ptr_id')


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
        'cgm.allocatednetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'AllocatedNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'cidr': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'family': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'pool': ('frontend.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Pool']"}),
            'usage': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'cgm.cgmgeneralconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'CgmGeneralConfig', '_ormbases': ['core.GeneralConfig']},
            'generalconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.GeneralConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'platform': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#platform'", 'blank': 'True'}),
            'router': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#router'", 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'cgm.dhcpnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'DHCPNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.ethernetinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'EthernetInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'eth_port': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#eth_port'"}),
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.interfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit_in': ('frontend.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#traffic_limits'", 'blank': 'True'}),
            'limit_out': ('frontend.registry.fields.SelectorKeyField', [], {'default': "''", 'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#traffic_limits'", 'blank': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_interfaceconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.networkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'NetworkConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('frontend.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'networks'", 'to': "orm['cgm.InterfaceConfig']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_networkconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.packageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PackageConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_packageconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.pppoenetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PPPoENetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'cgm.staticnetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'StaticNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'address': ('frontend.registry.fields.IPAddressField', [], {'subnet_required': 'True'}),
            'family': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'gateway': ('frontend.registry.fields.IPAddressField', [], {'host_required': 'True'}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.vpninterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'mac': ('frontend.registry.fields.MACAddressField', [], {'auto_add': 'True', 'max_length': '17'})
        },
        'cgm.vpnserverconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'VpnServerConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'protocol': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.vpn.server#protocol'"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_vpnserverconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.wifiinterfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiInterfaceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'antenna': ('frontend.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Antenna']", 'null': 'True'}),
            'antenna_connector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '11'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'wifi_radio': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_radio'"})
        },
        'cgm.wifinetworkconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiNetworkConfig', '_ormbases': ['cgm.NetworkConfig']},
            'bssid': ('frontend.registry.fields.MACAddressField', [], {'max_length': '17'}),
            'cidr': ('django.db.models.fields.IntegerField', [], {'default': '27'}),
            'essid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'family': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
            'networkconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.NetworkConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'pool': ('frontend.registry.fields.ModelSelectorKeyField', [], {'to': "orm['core.Pool']"}),
            'role': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#role'"}),
            'usage': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#usage'"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
        'core.antenna': {
            'Meta': {'object_name': 'Antenna'},
            'angle_horizontal': ('django.db.models.fields.IntegerField', [], {'default': '360'}),
            'angle_vertical': ('django.db.models.fields.IntegerField', [], {'default': '360'}),
            'gain': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_for': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'internal_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'polarization': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'core.generalconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'GeneralConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_core_generalconfig'", 'to': "orm['nodes.Node']"}),
            'type': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.general#type'"})
        },
        'core.pool': {
            'Meta': {'object_name': 'Pool'},
            'cidr': ('django.db.models.fields.IntegerField', [], {}),
            'default_prefix_len': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'family': ('frontend.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces.network#family'"}),
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
            'ant_external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ant_polarization': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ant_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'awaiting_renumber': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'border_router': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bssid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'captive_portal_status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'channel': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'clients': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'clients_so_far': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'conflicting_subnets': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dns_works': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'redundancy_link': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redundancy_req': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reported_uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'rtt_avg': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_max': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rtt_min': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'system_node': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thresh_frag': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'thresh_rts': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'uptime': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'uptime_last': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'uptime_so_far': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vpn_mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'vpn_mac_conf': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True'}),
            'vpn_server': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'warnings': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wifi_error_count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'wifi_mac': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
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
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Pool']"}),
            'pools': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['core.Pool']"}),
            'ssid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ssid_backbone': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ssid_mobile': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sticker': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dns.Zone']", 'null': 'True'})
        }
    }

    complete_apps = ['cgm']

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('cgm', '0041_polymorphic'),
    )

    def forwards(self, orm):
        db.rename_column('antennas_antennaequipmentconfig', 'content_type_id', 'polymorphic_ctype_id')

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")

    models = {
        'antennas.antenna': {
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
        'antennas.antennaequipmentconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'AntennaEquipmentConfig'},
            'antenna': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['antennas.Antenna']", 'on_delete': 'models.PROTECT'}),
            'azimuth': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'device': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'antennas'", 'to': "orm['cgm.WifiRadioDeviceConfig']"}),
            'elevation_angle': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_antennas.antennaequipmentconfig_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_antennas_antennaequipmentconfig'", 'to': "orm['core.Node']"}),
            'rotation': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'cgm.interfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceConfig'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_cgm.interfaceconfig_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_interfaceconfig'", 'to': "orm['core.Node']"})
        },
        'cgm.wifiradiodeviceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiRadioDeviceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'ack_distance': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'antenna_connector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '11'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'channel_width': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'interfaceconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.InterfaceConfig']", 'unique': 'True', 'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'wifi_radio': ('nodewatcher.core.registry.fields.SelectorKeyField', [], {'max_length': '50', 'regpoint': "'node.config'", 'enum_id': "'core.interfaces#wifi_radio'"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        }
    }

    complete_apps = ['antennas']
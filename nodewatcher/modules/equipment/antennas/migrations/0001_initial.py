# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('cgm', '0035_move_antenna'),
    )

    def forwards(self, orm):
        # Adding model 'AntennaEquipmentConfig'
        db.create_table('antennas_antennaequipmentconfig', (
            ('wifiradioequipmentconfig_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['equipment.WifiRadioEquipmentConfig'], unique=True, primary_key=True)),
            ('antenna', self.gf('nodewatcher.core.registry.fields.ModelSelectorKeyField')(to=orm['antennas.Antenna'], on_delete=models.PROTECT)),
            ('azimuth', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('elevation_angle', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('rotation', self.gf('django.db.models.fields.FloatField')(null=True)),
        ))
        db.send_create_signal('antennas', ['AntennaEquipmentConfig'])


    def backwards(self, orm):
        # Deleting model 'AntennaEquipmentConfig'
        db.delete_table('antennas_antennaequipmentconfig')


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
            'Meta': {'ordering': "['id']", 'object_name': 'AntennaEquipmentConfig', '_ormbases': ['equipment.WifiRadioEquipmentConfig']},
            'antenna': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['antennas.Antenna']", 'on_delete': 'models.PROTECT'}),
            'azimuth': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'elevation_angle': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rotation': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'wifiradioequipmentconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['equipment.WifiRadioEquipmentConfig']", 'unique': 'True', 'primary_key': 'True'})
        },
        'cgm.interfaceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterfaceConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_interfaceconfig'", 'to': "orm['nodes.Node']"})
        },
        'cgm.wifiradiodeviceconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiRadioDeviceConfig', '_ormbases': ['cgm.InterfaceConfig']},
            'antenna': ('nodewatcher.core.registry.fields.ModelSelectorKeyField', [], {'to': "orm['antennas.Antenna']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'antenna_connector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '11'}),
            'channel': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
        'equipment.wifiradioequipmentconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'WifiRadioEquipmentConfig'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'device': ('nodewatcher.core.registry.fields.IntraRegistryForeignKey', [], {'related_name': "'equipment'", 'to': "orm['cgm.WifiRadioDeviceConfig']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_equipment_wifiradioequipmentconfig'", 'to': "orm['nodes.Node']"})
        },
        'nodes.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        }
    }

    complete_apps = ['antennas']
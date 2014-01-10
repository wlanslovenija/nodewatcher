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
        pass

    def backwards(self, orm):
        pass

    models = {
        'cgm.packageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'PackageConfig'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'polymorphic_cgm.packageconfig_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'config_cgm_packageconfig'", 'to': "orm['core.Node']"})
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
        },
        'digitemp.digitemppackageconfig': {
            'Meta': {'ordering': "['id']", 'object_name': 'DigitempPackageConfig', '_ormbases': ['cgm.PackageConfig']},
            'packageconfig_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cgm.PackageConfig']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['digitemp']
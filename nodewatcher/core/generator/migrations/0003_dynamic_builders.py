# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('cgm', '0046_add_mobile_device'),
    )

    def forwards(self, orm):
        # Adding model 'Builder'
        db.create_table(u'generator_builder', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('platform', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('architecture', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(related_name='builders', blank=True, to=orm['generator.BuildVersion'])),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('private_key', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'generator', ['Builder'])

        # Adding unique constraint on 'Builder', fields ['platform', 'architecture', 'version']
        db.create_unique(u'generator_builder', ['platform', 'architecture', 'version_id'])

        # Adding model 'BuildChannel'
        db.create_table(u'generator_buildchannel', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'generator', ['BuildChannel'])

        # Adding M2M table for field builders on 'BuildChannel'
        m2m_table_name = db.shorten_name(u'generator_buildchannel_builders')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('buildchannel', models.ForeignKey(orm[u'generator.buildchannel'], null=False)),
            ('builder', models.ForeignKey(orm[u'generator.builder'], null=False))
        ))
        db.create_unique(m2m_table_name, ['buildchannel_id', 'builder_id'])

        # Adding model 'BuildVersion'
        db.create_table(u'generator_buildversion', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
        ))
        db.send_create_signal(u'generator', ['BuildVersion'])

        # Adding model 'BuildResult'
        db.create_table(u'generator_buildresult', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Node'])),
            ('config', self.gf('json_field.fields.JSONField')(default=u'null')),
            ('build_channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.BuildChannel'])),
            ('builder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Builder'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='pending', max_length=15)),
        ))
        db.send_create_signal(u'generator', ['BuildResult'])


    def backwards(self, orm):
        # Removing unique constraint on 'Builder', fields ['platform', 'architecture', 'version']
        db.delete_unique(u'generator_builder', ['platform', 'architecture', 'version_id'])

        # Deleting model 'Builder'
        db.delete_table(u'generator_builder')

        # Deleting model 'BuildChannel'
        db.delete_table(u'generator_buildchannel')

        # Removing M2M table for field builders on 'BuildChannel'
        db.delete_table(db.shorten_name(u'generator_buildchannel_builders'))

        # Deleting model 'BuildVersion'
        db.delete_table(u'generator_buildversion')

        # Deleting model 'BuildResult'
        db.delete_table(u'generator_buildresult')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.node': {
            'Meta': {'object_name': 'Node'},
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'})
        },
        u'generator.buildchannel': {
            'Meta': {'object_name': 'BuildChannel'},
            'builders': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'channels'", 'blank': 'True', 'to': u"orm['generator.Builder']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        u'generator.builder': {
            'Meta': {'unique_together': "(('platform', 'architecture', 'version'),)", 'object_name': 'Builder'},
            'architecture': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'platform': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'private_key': ('django.db.models.fields.TextField', [], {}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'builders'", 'blank': 'True', 'to': u"orm['generator.BuildVersion']"})
        },
        u'generator.buildresult': {
            'Meta': {'object_name': 'BuildResult'},
            'build_channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.BuildChannel']"}),
            'builder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['generator.Builder']"}),
            'config': ('json_field.fields.JSONField', [], {'default': "u'null'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Node']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '15'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        u'generator.buildversion': {
            'Meta': {'object_name': 'BuildVersion'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        }
    }

    complete_apps = ['generator']
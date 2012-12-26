# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("nodes", "0008_remove_old"),
    )

    def forwards(self, orm):
        # Deleting model 'TrafficControlClass'
        db.delete_table('policy_trafficcontrolclass')

        # Deleting model 'PolicyJob'
        db.delete_table('policy_policyjob')

        # Deleting model 'Policy'
        db.delete_table('policy_policy')

    def backwards(self, orm):
        # Adding model 'TrafficControlClass'
        db.create_table('policy_trafficcontrolclass', (
            ('bandwidth', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('policy', ['TrafficControlClass'])

        # Adding model 'PolicyJob'
        db.create_table('policy_policyjob', (
            ('node', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('addr', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('family', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('policy', ['PolicyJob'])

        # Adding model 'Policy'
        db.create_table('policy_policy', (
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(related_name='gw_policy', to=orm['nodes.Node'])),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('addr', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('family', self.gf('django.db.models.fields.IntegerField')()),
            ('action', self.gf('django.db.models.fields.IntegerField')()),
            ('tc_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['policy.TrafficControlClass'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('policy', ['Policy'])

    models = {

    }

    complete_apps = ['policy']

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
        # Deleting model 'ProjectPackage'
        db.delete_table('generator_projectpackage')

        # Deleting model 'Template'
        db.delete_table('generator_template')

        # Removing M2M table for field imagefiles on 'Template'
        db.delete_table('generator_template_imagefiles')

        # Deleting model 'IfaceTemplate'
        db.delete_table('generator_ifacetemplate')

        # Deleting model 'ImageFile'
        db.delete_table('generator_imagefile')

        # Deleting model 'Profile'
        db.delete_table('generator_profile')

        # Removing M2M table for field optional_packages on 'Profile'
        db.delete_table('generator_profile_optional_packages')

        # Deleting model 'OptionalPackage'
        db.delete_table('generator_optionalpackage')

        # Deleting model 'ProfileAdaptationChain'
        db.delete_table('generator_profileadaptationchain')

    def backwards(self, orm):
        # Adding model 'ProjectPackage'
        db.create_table('generator_projectpackage', (
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='packages', to=orm['nodes.Project'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('generator', ['ProjectPackage'])

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
            ('experimental', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('imagebuilder', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('arch', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('channel', self.gf('django.db.models.fields.IntegerField')()),
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

        # Adding model 'ImageFile'
        db.create_table('generator_imagefile', (
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('generator', ['ImageFile'])

        # Adding model 'Profile'
        db.create_table('generator_profile', (
            ('node', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['nodes.Node'], unique=True)),
            ('root_pass', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('use_vpn', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('lan_bridge', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('wan_gw', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wan_cidr', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('antenna', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('vpn_egress_limit', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('wan_ip', self.gf('django.db.models.fields.CharField')(max_length=40, null=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['generator.Template'])),
            ('wan_dhcp', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('channel', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('generator', ['Profile'])

        # Adding M2M table for field optional_packages on 'Profile'
        db.create_table('generator_profile_optional_packages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profile', models.ForeignKey(orm['generator.profile'], null=False)),
            ('optionalpackage', models.ForeignKey(orm['generator.optionalpackage'], null=False))
        ))
        db.create_unique('generator_profile_optional_packages', ['profile_id', 'optionalpackage_id'])

        # Adding model 'OptionalPackage'
        db.create_table('generator_optionalpackage', (
            ('fancy_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('generator', ['OptionalPackage'])

        # Adding model 'ProfileAdaptationChain'
        db.create_table('generator_profileadaptationchain', (
            ('class_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='adaptation_chain', to=orm['generator.Template'])),
        ))
        db.send_create_signal('generator', ['ProfileAdaptationChain'])

    models = {

    }

    complete_apps = ['generator']

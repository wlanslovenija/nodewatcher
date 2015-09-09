# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields
import json_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnotherRegistryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('interesting', models.CharField(default=b'nope', max_length=30, null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_registry_tests.anotherregistryitem_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MultipleRegistryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('foo', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RelatedModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('level', nodewatcher.core.registry.fields.RegistryChoiceField(b'thing.first', b'foo.simple#level', max_length=50, null=True, choices=[(b'level-x', b'Level 0'), (b'level-a', b'Level 1'), (b'level-m', b'Level 2')])),
            ],
        ),
        migrations.CreateModel(
            name='SimpleRegistryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('interesting', models.CharField(default=b'nope', max_length=30, null=True)),
                ('level', nodewatcher.core.registry.fields.RegistryChoiceField(b'thing.first', b'foo.simple#level', max_length=50, null=True, choices=[(b'level-x', b'Level 0'), (b'level-a', b'Level 1'), (b'level-m', b'Level 2')])),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Thing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('foo', models.CharField(max_length=30, null=True)),
                ('bar', models.IntegerField(null=True)),
                ('registry_metadata', json_field.fields.JSONField(default={}, help_text='Enter a valid JSON object', editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='ChildRegistryItem',
            fields=[
                ('simpleregistryitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='registry_tests.SimpleRegistryItem')),
                ('additional', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('registry_tests.simpleregistryitem',),
        ),
        migrations.CreateModel(
            name='FirstSubRegistryItem',
            fields=[
                ('multipleregistryitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='registry_tests.MultipleRegistryItem')),
                ('bar', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('registry_tests.multipleregistryitem',),
        ),
        migrations.CreateModel(
            name='SecondSubRegistryItem',
            fields=[
                ('multipleregistryitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='registry_tests.MultipleRegistryItem')),
                ('moo', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('registry_tests.multipleregistryitem',),
        ),
        migrations.CreateModel(
            name='ThirdSubRegistryItem',
            fields=[
                ('multipleregistryitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='registry_tests.MultipleRegistryItem')),
                ('moo', models.IntegerField(null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('registry_tests.multipleregistryitem',),
        ),
        migrations.AddField(
            model_name='simpleregistryitem',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_registry_tests.simpleregistryitem_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='simpleregistryitem',
            name='root',
            field=models.ForeignKey(related_name='first_registry_tests_simpleregistryitem', editable=False, to='registry_tests.Thing'),
        ),
        migrations.AddField(
            model_name='multipleregistryitem',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_registry_tests.multipleregistryitem_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='multipleregistryitem',
            name='root',
            field=models.ForeignKey(related_name='second_registry_tests_multipleregistryitem', editable=False, to='registry_tests.Thing'),
        ),
        migrations.AddField(
            model_name='anotherregistryitem',
            name='root',
            field=models.ForeignKey(related_name='first_registry_tests_anotherregistryitem', editable=False, to='registry_tests.Thing'),
        ),
        migrations.CreateModel(
            name='DoubleChildRegistryItem',
            fields=[
                ('childregistryitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='registry_tests.ChildRegistryItem')),
                ('another', models.IntegerField(default=17, null=True)),
                ('related', models.ForeignKey(to='registry_tests.RelatedModel', null=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=('registry_tests.childregistryitem',),
        ),
    ]

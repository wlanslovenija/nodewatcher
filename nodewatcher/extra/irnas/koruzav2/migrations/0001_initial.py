# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-29 12:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0008_auto_20160821_0625'),
    ]

    operations = [
        migrations.CreateModel(
            name='KoruzaMonitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_order', models.IntegerField(editable=False, null=True)),
                ('annotations', models.TextField(default='{}', editable=False)),
                ('mcu_connected', models.NullBooleanField()),
                ('motor_x', models.IntegerField(null=True)),
                ('motor_y', models.IntegerField(null=True)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_irnas_koruzav2.koruzamonitor_set+', to='contenttypes.ContentType')),
                ('root', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='monitoring_irnas_koruzav2_koruzamonitor', to='core.Node')),
            ],
            options={
                'ordering': ['display_order', 'id'],
                'abstract': False,
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0002_auto_20150921_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientmonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='generalmonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='generalresourcesmonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='interfacemonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='networkaddressmonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='networkresourcesmonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='routingannouncemonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='routingtopologymonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='rttmeasurementmonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='systemstatusmonitor',
            name='display_order',
            field=models.IntegerField(null=True),
        ),
    ]

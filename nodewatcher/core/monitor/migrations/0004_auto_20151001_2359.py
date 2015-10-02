# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0003_auto_20151001_2341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientmonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='generalmonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='generalresourcesmonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='interfacemonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='networkaddressmonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='networkresourcesmonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='routingannouncemonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='rttmeasurementmonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='systemstatusmonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='wifiinterfacemonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='clientmonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='generalmonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='generalresourcesmonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='interfacemonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='networkaddressmonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='networkresourcesmonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='routingannouncemonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='routingtopologymonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='rttmeasurementmonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='systemstatusmonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0005_interfacemonitor_up'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='generalmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='generalresourcesmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='interfacemonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='networkaddressmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='networkresourcesmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='routingannouncemonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='routingtopologymonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='rttmeasurementmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
        migrations.AlterField(
            model_name='systemstatusmonitor',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
    ]

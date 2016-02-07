# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0005_interfacemonitor_up'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientmonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='generalmonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='generalresourcesmonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='interfacemonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='networkaddressmonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='networkresourcesmonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='routingannouncemonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='routingtopologymonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='rttmeasurementmonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='systemstatusmonitor',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
    ]

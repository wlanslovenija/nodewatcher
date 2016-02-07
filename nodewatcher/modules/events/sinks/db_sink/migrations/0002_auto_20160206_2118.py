# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('events_sinks_database', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serializednodeevent',
            name='record',
            field=jsonfield.fields.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='serializednodewarning',
            name='record',
            field=jsonfield.fields.JSONField(null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events_sinks_database', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serializednodeevent',
            name='record',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='serializednodewarning',
            name='record',
            field=models.TextField(null=True),
        ),
    ]

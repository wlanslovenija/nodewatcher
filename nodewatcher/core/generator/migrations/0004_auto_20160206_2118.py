# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('generator', '0003_builder_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='builder',
            name='metadata',
            field=jsonfield.fields.JSONField(editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='buildresult',
            name='config',
            field=jsonfield.fields.JSONField(help_text='Configuration used to build this firmware.', blank=True),
        ),
    ]

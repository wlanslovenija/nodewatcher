# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('unknown_nodes', '0002_unknownnode_origin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unknownnode',
            name='certificate',
            field=jsonfield.fields.JSONField(null=True),
        ),
    ]

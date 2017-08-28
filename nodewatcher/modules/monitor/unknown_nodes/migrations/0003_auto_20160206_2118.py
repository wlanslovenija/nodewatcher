# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('unknown_nodes', '0002_unknownnode_origin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unknownnode',
            name='certificate',
            field=models.TextField(null=True),
        ),
    ]

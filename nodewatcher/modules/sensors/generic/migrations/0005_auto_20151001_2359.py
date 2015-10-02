# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sensors_generic', '0004_genericsensormonitor_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='genericsensormonitor',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='genericsensormonitor',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]

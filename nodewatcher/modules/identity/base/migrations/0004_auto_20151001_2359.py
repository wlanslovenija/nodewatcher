# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('identity_base', '0003_auto_20151001_2341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='identityconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='identitymechanismconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='identityconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='identitymechanismconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]

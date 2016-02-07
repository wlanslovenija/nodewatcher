# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('identity_base', '0004_auto_20151001_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identityconfig',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
        migrations.AlterField(
            model_name='identitymechanismconfig',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
    ]

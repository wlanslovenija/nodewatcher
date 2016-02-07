# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('services_dhcp', '0004_auto_20151001_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dhcpleaseconfig',
            name='annotations',
            field=jsonfield.fields.JSONField(default={}, editable=False),
        ),
    ]

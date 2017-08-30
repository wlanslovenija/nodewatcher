# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services_dns', '0004_auto_20151001_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dnsserverconfig',
            name='annotations',
            field=models.TextField(default='{}', editable=False),
        ),
    ]

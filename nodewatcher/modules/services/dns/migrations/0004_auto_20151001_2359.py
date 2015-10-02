# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services_dns', '0003_dnsserverconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dnsserverconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='dnsserverconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]

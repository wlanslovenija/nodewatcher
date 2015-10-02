# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services_dhcp', '0003_dhcpleaseconfig_display_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dhcpleaseconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='dhcpleaseconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]

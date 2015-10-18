# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_ippool_top_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ippool',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, editable=False, to='core.IpPool', null=True),
        ),
        migrations.AlterField(
            model_name='ippool',
            name='top_level',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to='core.IpPool', null=True),
        ),
    ]

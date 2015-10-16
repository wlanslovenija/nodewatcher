# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populate_toplevel(apps, schema_editor):
    """
    Populates the top_level field for existing IpPool instances.
    """

    IpPool = apps.get_model('core', 'IpPool')
    for ip_pool in IpPool.objects.all():
        pool = ip_pool
        while True:
            if pool.parent is None:
                break
            pool = pool.parent

        ip_pool.top_level = pool
        ip_pool.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20151001_2359'),
    ]

    operations = [
        migrations.AddField(
            model_name='ippool',
            name='top_level',
            field=models.ForeignKey(related_name='+', blank=True, to='core.IpPool', null=True),
        ),
        migrations.RunPython(populate_toplevel, reverse_code=migrations.RunPython.noop),
    ]

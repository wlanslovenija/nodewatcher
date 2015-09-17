# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodewatcher.core.registry.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='throughputinterfacelimitconfig',
            name='limit_in',
            field=nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.limits#speeds', default=b'', max_length=50, verbose_name='Download limit', blank=True, choices=[(b'128', '128 Kbit/s'), (b'256', '256 Kbit/s'), (b'512', '512 Kbit/s'), (b'1024', '1 Mbit/s'), (b'2048', '2 Mbit/s'), (b'4096', '4 Mbit/s'), (b'6144', '6 Mbit/s'), (b'8192', '8 Mbit/s'), (b'10240', '10 Mbit/s'), (b'15360', '15 Mbit/s'), (b'20480', '20 Mbit/s'), (b'25600', '25 Mbit/s'), (b'30720', '30 Mbit/s'), (b'40960', '40 Mbit/s'), (b'51200', '50 Mbit/s'), (b'61440', '60 Mbit/s'), (b'71680', '70 Mbit/s'), (b'81920', '80 Mbit/s'), (b'92160', '90 Mbit/s'), (b'102400', '100 Mbit/s')]),
        ),
        migrations.AlterField(
            model_name='throughputinterfacelimitconfig',
            name='limit_out',
            field=nodewatcher.core.registry.fields.RegistryChoiceField(b'node.config', b'core.interfaces.limits#speeds', default=b'', max_length=50, verbose_name='Upload limit', blank=True, choices=[(b'128', '128 Kbit/s'), (b'256', '256 Kbit/s'), (b'512', '512 Kbit/s'), (b'1024', '1 Mbit/s'), (b'2048', '2 Mbit/s'), (b'4096', '4 Mbit/s'), (b'6144', '6 Mbit/s'), (b'8192', '8 Mbit/s'), (b'10240', '10 Mbit/s'), (b'15360', '15 Mbit/s'), (b'20480', '20 Mbit/s'), (b'25600', '25 Mbit/s'), (b'30720', '30 Mbit/s'), (b'40960', '40 Mbit/s'), (b'51200', '50 Mbit/s'), (b'61440', '60 Mbit/s'), (b'71680', '70 Mbit/s'), (b'81920', '80 Mbit/s'), (b'92160', '90 Mbit/s'), (b'102400', '100 Mbit/s')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cgm', '0009_auto_20151001_2341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='allocatednetworkconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='authenticationconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='bridgednetworkconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='bridgeinterfaceconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='cgmgeneralconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='dhcpnetworkconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='ethernetinterfaceconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='interfaceconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='interfacelimitconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='mobileinterfaceconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='networkconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='packageconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='passwordauthenticationconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='pppoenetworkconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='staticnetworkconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='throughputinterfacelimitconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='wifiinterfaceconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='wifiradiodeviceconfig',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterField(
            model_name='authenticationconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='interfaceconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='interfacelimitconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='networkconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='packageconfig',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]

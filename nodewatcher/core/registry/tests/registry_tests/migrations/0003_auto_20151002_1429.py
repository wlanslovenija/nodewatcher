# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registry_tests', '0002_auto_20150921_1818'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='anotherregistryitem',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='childregistryitem',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='doublechildregistryitem',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='firstsubregistryitem',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='multipleregistryitem',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='secondsubregistryitem',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='simpleregistryitem',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AlterModelOptions(
            name='thirdsubregistryitem',
            options={'ordering': ['display_order', 'id']},
        ),
        migrations.AddField(
            model_name='anotherregistryitem',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='multipleregistryitem',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='simpleregistryitem',
            name='display_order',
            field=models.IntegerField(null=True, editable=False),
        ),
    ]

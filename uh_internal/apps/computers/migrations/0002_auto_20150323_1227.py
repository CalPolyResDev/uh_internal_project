# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import resnet_internal.apps.computers.fields


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='computer',
            name='location',
            field=models.CharField(default='', verbose_name='Location', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pinhole',
            name='udp_ports',
            field=resnet_internal.apps.computers.fields.ListField(verbose_name='UDP Ports'),
            preserve_default=True,
        ),
    ]

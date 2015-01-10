# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0002_auto_20150110_0010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computer',
            name='property_id',
            field=models.CharField(unique=True, default=None, verbose_name='Cal Poly Property ID', max_length=50, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='computer',
            name='serial_number',
            field=models.CharField(unique=True, default=None, verbose_name='Serial Number', max_length=20, blank=True, null=True),
            preserve_default=True,
        ),
    ]

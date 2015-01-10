# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computer',
            name='property_id',
            field=models.CharField(null=True, unique=True, blank=True, max_length=50, verbose_name='Cal Poly Property ID'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='computer',
            name='serial_number',
            field=models.CharField(null=True, unique=True, blank=True, max_length=20, verbose_name='Serial Number'),
            preserve_default=True,
        ),
    ]

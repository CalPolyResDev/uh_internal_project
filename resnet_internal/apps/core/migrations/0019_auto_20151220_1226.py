# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20151214_0100'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='building',
            options={},
        ),
        migrations.AlterModelOptions(
            name='community',
            options={'verbose_name_plural': 'Communities'},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={},
        ),
        migrations.AlterModelOptions(
            name='subdepartment',
            options={'verbose_name': 'Sub Department'},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20151020_1728'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='room',
            options={'verbose_name': 'University Housing Room'},
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(verbose_name='Room Number', max_length=10),
        ),
    ]

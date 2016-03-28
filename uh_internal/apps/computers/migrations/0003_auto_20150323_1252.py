# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0002_auto_20150323_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computer',
            name='location',
            field=models.CharField(verbose_name='Location', max_length=100, blank=True, null=True),
            preserve_default=True,
        ),
    ]

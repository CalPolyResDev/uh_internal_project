# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='printer',
            name='location',
            field=models.CharField(default='', verbose_name='Location', max_length=100),
            preserve_default=False,
        ),
    ]

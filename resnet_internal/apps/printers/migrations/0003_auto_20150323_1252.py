# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0002_printer_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printer',
            name='location',
            field=models.CharField(verbose_name='Location', max_length=100, blank=True, null=True),
            preserve_default=True,
        ),
    ]

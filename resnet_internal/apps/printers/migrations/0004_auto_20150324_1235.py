# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('printers', '0003_auto_20150323_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='printer',
            name='dhcp',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='printer',
            name='ip_address',
            field=models.GenericIPAddressField(unique=True, blank=True, protocol='IPv4', verbose_name='IP Address', null=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computers', '0006_auto_20150708_1743'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='computer',
            options={},
        ),
        migrations.AlterModelOptions(
            name='domainname',
            options={'verbose_name': 'Domain Name'},
        ),
        migrations.AlterModelOptions(
            name='pinhole',
            options={},
        ),
    ]

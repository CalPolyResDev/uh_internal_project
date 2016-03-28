# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_networkdevice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='networkdevice',
            name='ip_address',
            field=models.GenericIPAddressField(verbose_name='IP Address'),
        ),
    ]

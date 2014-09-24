# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20140911_1344'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='community',
            options={'verbose_name': 'Community', 'verbose_name_plural': 'Communities'},
        ),
    ]

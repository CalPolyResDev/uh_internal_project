# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0007_auto_20151220_1213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='port',
            name='vlan',
        ),
    ]

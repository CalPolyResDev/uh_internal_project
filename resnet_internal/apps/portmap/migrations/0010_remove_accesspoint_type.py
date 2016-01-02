# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0009_accesspoint_ap_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accesspoint',
            name='type',
        ),
    ]

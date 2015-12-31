# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0004_auto_20151020_1742'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reshallwired',
            name='room',
        ),
        migrations.RenameField('reshallwired', 'room_new', 'room'),
    ]

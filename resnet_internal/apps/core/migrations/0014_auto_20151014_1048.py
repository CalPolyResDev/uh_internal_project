# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20151013_1249'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adgroup',
            old_name='common_name',
            new_name='display_name',
        ),
    ]

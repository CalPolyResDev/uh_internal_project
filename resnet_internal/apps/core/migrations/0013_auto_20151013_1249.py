# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20151011_1550'),
    ]

    operations = [
        migrations.RenameField(
            model_name='navbarlink',
            old_name='url',
            new_name='external_url',
        ),
        migrations.RemoveField(
            model_name='navbarlink',
            name='open_in_new',
        ),
    ]

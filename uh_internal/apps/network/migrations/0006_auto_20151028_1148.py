# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portmap', '0005_auto_20151020_1749'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reshallwired',
            name='building',
        ),
        migrations.RemoveField(
            model_name='reshallwired',
            name='community',
        ),
        migrations.AlterField(
            model_name='reshallwired',
            name='room',
            field=models.ForeignKey(to='core.Room', verbose_name='Room', null=True),
        ),
    ]

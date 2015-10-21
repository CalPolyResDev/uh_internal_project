# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20151020_1728'),
        ('portmap', '0002_accesspoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='reshallwired',
            name='room_new',
            field=models.ForeignKey(to='core.Room', verbose_name='Room New', null=True),
        ),
    ]

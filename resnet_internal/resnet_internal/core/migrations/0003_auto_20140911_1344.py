# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20140911_1328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='building',
            name='community',
        ),
        migrations.DeleteModel(
            name='Building',
        ),
        migrations.DeleteModel(
            name='Community',
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
            ],
            options={
                'verbose_name': 'Building',
                'db_table': 'building',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Community',
            fields=[
            ],
            options={
                'verbose_name': 'Community',
                'db_table': 'community',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]

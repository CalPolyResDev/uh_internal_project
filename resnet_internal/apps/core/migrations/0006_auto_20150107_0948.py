# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20141013_1158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailyduties',
            name='last_user',
        ),
        migrations.DeleteModel(
            name='DailyDuties',
        ),
        migrations.AlterModelOptions(
            name='community',
            options={'verbose_name': 'Community', 'verbose_name_plural': 'Communities', 'managed': False},
        ),
        migrations.AlterModelOptions(
            name='techflair',
            options={'verbose_name': 'Tech Flair', 'verbose_name_plural': 'Tech Flair'},
        ),
    ]

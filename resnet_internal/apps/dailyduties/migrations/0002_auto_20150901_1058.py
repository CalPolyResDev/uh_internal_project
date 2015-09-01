# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dailyduties', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dailyduties',
            options={'verbose_name': 'Daily Duty', 'verbose_name_plural': 'Daily Duties'},
        ),
        migrations.AlterField(
            model_name='dailyduties',
            name='last_user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True, verbose_name='Last User to Check'),
        ),
    ]

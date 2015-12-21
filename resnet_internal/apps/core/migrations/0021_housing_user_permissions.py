# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20151220_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='resnetinternaluser',
            name='is_csd',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resnetinternaluser',
            name='is_fd_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resnetinternaluser',
            name='is_ra',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resnetinternaluser',
            name='is_ral',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resnetinternaluser',
            name='is_ral_manager',
            field=models.BooleanField(default=False),
        ),
    ]

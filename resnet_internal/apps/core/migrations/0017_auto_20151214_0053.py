# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20151203_2229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='sub_departments',
        ),
        migrations.AddField(
            model_name='subdepartment',
            name='department',
            field=models.ForeignKey(null=True, related_name='sub_departments', verbose_name='Department', to='core.Community'),
        ),
    ]
